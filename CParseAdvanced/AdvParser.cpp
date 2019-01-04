#include <iostream>
#include <stdio.h>
#include <cstring>
#include <cmath>
#include <fstream>
#include <string>
#include <regex>
#include <iterator>
#include <python3.7m/Python.h>
#include <boost/python.hpp>
#include <boost/python/numpy.hpp>

#include <boost/python/suite/indexing/vector_indexing_suite.hpp>
#include <boost/python/module.hpp>
#include <boost/python/def.hpp>
#include <boost/python/implicit.hpp>
#include <boost/python/extract.hpp>

namespace p = boost::python;
namespace np = boost::python::numpy;

struct AdvParser
{
    bool checkBase = true;
    bool checkNodes = true;
    bool shapeCreated = true;
    int xnodes, ynodes, znodes;
    double xbase, ybase, zbase;
    std::string def_ext;
    AdvParser()
    {
        xnodes = 0;
        ynodes = 0;
        znodes = 0;

        xbase = 0.0;
        ybase = 0.0;
        zbase = 0.0;

        def_ext = ".omf";
    };

    void setXnodes(int val) { this->xnodes = val; }
    void setYnodes(int val) { this->ynodes = val; }
    void setZnodes(int val) { this->znodes = val; }
    void setXbase(int val) { this->xbase = val; }
    void setYbase(int val) { this->ybase = val; }
    void setZbase(int val) { this->zbase = val; }
    int getXnodes() { return xnodes; }
    int getYnodes() { return ynodes; }
    int getZnodes() { return znodes; }
    double getXbase() { return xbase; }
    double getYbase() { return ybase; }
    double getZbase() { return zbase; }

    int getMifHeader(std::ifstream &miffile)
    {
        std::string line;
        int buffer_size = 0;

        std::string node_reg("# xnodes:");
        std::string base_reg("# xbase:");

        if (miffile.is_open())
        {
            while (std::getline(miffile, line))
            {
                if (line.at(0) == '#')
                {
                    if (line == "# Begin: Data Binary 8")
                    {
                        buffer_size = 8;
                        break;
                    }
                    else if (line == "# Begin: Data Binary 4")
                    {
                        buffer_size = 4;
                    }

                    if (checkNodes && line.substr(0, node_reg.length()) == node_reg)
                    {

                        if (node_reg.at(2) == 'x')
                        {
                            xnodes = std::stoi(line.substr(node_reg.length(), line.length()));
                            node_reg.at(2) = 'y';
                        }
                        else if (node_reg.at(2) == 'y')
                        {
                            ynodes = std::stoi(line.substr(node_reg.length(), line.length()));
                            node_reg.at(2) = 'z';
                        }
                        else
                        {
                            znodes = std::stoi(line.substr(node_reg.length(), line.length()));
                            checkNodes = false;
                        }
                    }
                    if (checkBase && line.substr(0, base_reg.length()) == base_reg)
                    {

                        if (base_reg.at(2) == 'x')
                        {
                            xbase = std::stod(line.substr(base_reg.length(), line.length()));
                            base_reg.at(2) = 'y';
                        }
                        else if (base_reg.at(2) == 'y')
                        {
                            ybase = std::stod(line.substr(base_reg.length(), line.length()));
                            base_reg.at(2) = 'z';
                        }
                        else
                        {
                            zbase = std::stod(line.substr(base_reg.length(), line.length()));
                            checkBase = false;
                        }
                    }
                }
                else
                    break;
            }
            if (buffer_size <= 0)
            {
                throw "Invalid buffer size";
            }
            char IEEE_BUF[buffer_size];

            miffile.read(IEEE_BUF, buffer_size);

            double *IEEE_val = (double *)IEEE_BUF;
            if (IEEE_val[0] != 123456789012345.0)
            {
                throw "IEEE value not consistent";
            }
            return buffer_size;
        }
        else
        {
            throw std::runtime_error("Invalid mif file");
        }
        return 0;
    }

    void matrix_vector_mul(double mat[3][3], double vec[3])
    {
        // only 3 x 1, inplace
        double c[3] = {vec[0], vec[1], vec[2]};
        vec[0] = mat[0][0] * c[0] + mat[0][1] * c[1] + mat[0][2] * c[2];
        vec[1] = mat[1][0] * c[0] + mat[1][1] * c[1] + mat[1][2] * c[2];
        vec[2] = mat[2][0] * c[0] + mat[2][1] * c[1] + mat[2][2] * c[2];
    }

    void matrix_vector_cpy(double mat[3][3], double c[3], double vec[3])
    {
        // only 3 x 1, not inplace
        vec[0] = mat[0][0] * c[0] + mat[0][1] * c[1] + mat[0][2] * c[2];
        vec[1] = mat[1][0] * c[0] + mat[1][1] * c[1] + mat[1][2] * c[2];
        vec[2] = mat[2][0] * c[0] + mat[2][1] * c[1] + mat[2][2] * c[2];
    }

    void generateVectors(double *vbo,
                         int *offset,
                         double position[3],
                         double vector[3], // from omf
                         double t_rotation[3][3],
                         double height,
                         double radius,
                         int resolution)
    {
        double height_operator[3] = {0, 0, height * 1.5};
        double phi = acos(vector[2]);               // z rot
        double theta = atan2(vector[1], vector[0]); // y rot
        double ct = cos(theta);
        double st = sin(theta);
        double cp = cos(phi);
        double sp = sin(phi);
        double rotation_matrix[3][3] = {
            {ct, -st * cp, st * sp},
            {st, cp * ct, -sp * ct},
            {0, sp, cp}};
        double origin_base[3], tmp_operator[12], cpy[3];
        double cyllinder_co_rot[3] = {radius, radius, 0};
        double cone_co_rot[3] = {2 * radius, 2 * radius, 0};
        std::memcpy(origin_base, position, sizeof(double) * 3);

        for (int i = 0; i < resolution - 1; i++)
        {
            // bottom triangle - cyllinder
            matrix_vector_cpy(rotation_matrix, cyllinder_co_rot, cpy);
            tmp_operator[0] = origin_base[0] + cpy[0];
            tmp_operator[1] = origin_base[1] + cpy[1];
            tmp_operator[2] = origin_base[2] + cpy[2];

            // bottom triangle - cone
            matrix_vector_cpy(rotation_matrix, cone_co_rot, cpy);
            cpy[2] += height;
            tmp_operator[3] = origin_base[0] + cpy[0];
            tmp_operator[4] = origin_base[1] + cpy[1];
            tmp_operator[5] = origin_base[2] + cpy[2];

            // top triangle - cyllinder
            matrix_vector_cpy(rotation_matrix, cyllinder_co_rot, cpy);
            cpy[2] += height;
            tmp_operator[6] = origin_base[0] + cpy[0];
            tmp_operator[7] = origin_base[1] + cpy[1];
            tmp_operator[8] = origin_base[2] + cpy[2];

            // top triangle - cone
            matrix_vector_mul(rotation_matrix, height_operator);
            tmp_operator[9] = origin_base[0] + height_operator[0];
            tmp_operator[10] = origin_base[1] + height_operator[1];
            tmp_operator[11] = origin_base[2] + height_operator[2];
            height_operator[0] = 0;
            height_operator[1] = 0;
            height_operator[2] = 1.5 * height;
            matrix_vector_mul(t_rotation, cyllinder_co_rot);
            matrix_vector_mul(t_rotation, cone_co_rot);

            std::memcpy(vbo + *offset, tmp_operator, 12 * sizeof(double));
            *offset += 12;
        }
        // reset roational vectors to its defaults

        cyllinder_co_rot[0] = radius;
        cyllinder_co_rot[1] = radius;
        cyllinder_co_rot[2] = 0;
        matrix_vector_mul(rotation_matrix, cyllinder_co_rot);
        tmp_operator[0] = origin_base[0] + cyllinder_co_rot[0];
        tmp_operator[1] = origin_base[1] + cyllinder_co_rot[1];
        tmp_operator[2] = origin_base[2] + cyllinder_co_rot[2];

        cone_co_rot[0] = 2 * radius;
        cone_co_rot[1] = 2 * radius;
        cone_co_rot[2] = height;
        matrix_vector_mul(rotation_matrix, cone_co_rot);
        tmp_operator[3] = origin_base[0] + cone_co_rot[0];
        tmp_operator[4] = origin_base[1] + cone_co_rot[1];
        tmp_operator[5] = origin_base[2] + cone_co_rot[2];

        cyllinder_co_rot[0] = radius;
        cyllinder_co_rot[1] = radius;
        cyllinder_co_rot[2] = height;
        matrix_vector_mul(rotation_matrix, cyllinder_co_rot);
        tmp_operator[6] = origin_base[0] + cyllinder_co_rot[0];
        tmp_operator[7] = origin_base[1] + cyllinder_co_rot[1];
        tmp_operator[8] = origin_base[2] + cyllinder_co_rot[2];

        height_operator[0] = 0;
        height_operator[1] = 0;
        height_operator[2] = 1.5 * height;
        matrix_vector_mul(rotation_matrix, height_operator);
        tmp_operator[9] = origin_base[0] + height_operator[0];
        tmp_operator[10] = origin_base[1] + height_operator[1];
        tmp_operator[11] = origin_base[2] + height_operator[2];
        std::memcpy(vbo + *offset, tmp_operator, 12 * sizeof(double));
        *offset += 12;
    }

    void generateCubes(double *sh, double position[3], double dimensions[3], int current_pos)
    {
        double arr[72] = {
            //TOP FACE
            position[0] + dimensions[0], position[1], position[2] + dimensions[2],
            position[0], position[1], position[2] + dimensions[2],
            position[0], position[1] + dimensions[1], position[2] + dimensions[2],
            position[0] + dimensions[0], position[1] + dimensions[1], position[2] + dimensions[2],
            //BOTTOM FACE
            position[0] + dimensions[0], position[1], position[2],
            position[0], position[1], position[2],
            position[0], position[1] + dimensions[1], position[2],
            position[0] + dimensions[0], position[1] + dimensions[1], position[2],
            //FRONT FACE
            position[0] + dimensions[0], position[1] + dimensions[1], position[2] + dimensions[2],
            position[0], position[1] + dimensions[1], position[2] + dimensions[2],
            position[0], position[1] + dimensions[1], position[2],
            position[0] + dimensions[0], position[1] + dimensions[1], position[2],
            //BACK FACE
            position[0] + dimensions[0], position[1], position[2] + dimensions[2],
            position[0], position[1], position[2] + dimensions[2],
            position[0], position[1], position[2],
            position[0] + dimensions[0], position[1], position[2],
            //RIGHT FACE
            position[0] + dimensions[0], position[1], position[2] + dimensions[2],
            position[0] + dimensions[0], position[1] + dimensions[1], position[2] + dimensions[2],
            position[0] + dimensions[0], position[1] + dimensions[1], position[2],
            position[0] + dimensions[0], position[1], position[2],
            //LEFT FACE
            position[0], position[1] + dimensions[1], position[2] + dimensions[2],
            position[0], position[1], position[2] + dimensions[2],
            position[0], position[1], position[2],
            position[0], position[1] + dimensions[1], position[2]};
        std::memcpy(sh + current_pos, arr, sizeof(double) * 72);
    }

    np::ndarray generateIndices(int N, int index_required)
    {
        uint32_t start_index = 0;
        uint32_t *indices = (uint32_t *)malloc(sizeof(uint32_t) * (3 * (index_required - 2) * N));
        for (uint32_t n = 0; n < N; n++)
        {
            start_index = n * index_required * 3;
            for (uint32_t i = 0; i < (index_required - 2) * 3; i += 3)
            {
                indices[n * index_required + i + 0] = start_index + i - 3;
                indices[n * index_required + i + 1] = start_index + i - 2;
                indices[n * index_required + i + 2] = start_index + i - 1;
            }
        }
        np::dtype dt = np::dtype::get_builtin<uint32_t>();
        p::tuple shape = p::make_tuple(3 * (index_required - 2) * N);
        p::tuple stride = p::make_tuple(sizeof(uint32_t));
        return np::from_data(indices,
                             dt,
                             shape,
                             stride,
                             p::object());
    }
    np::ndarray getCubeOutline(int xn, int yn, int zn,
                               double xb, double yb, double zb,
                               int per_vertex)
    {
        double *sh = (double *)(malloc(sizeof(double) * xn * yn * zn * per_vertex));
        double dimensions[3] = {xb, yb, zb};
        int current_pos = 0;
        for (int z = 0; z < zn; z++)
        {
            for (int y = 0; y < yn; y++)
            {
                for (int x = 0; x < xn; x++)
                {
                    double position[3] = {xb * (x % xn) - xn * xb / 2,
                                          yb * (y % yn) - yn * yb / 2,
                                          zb * (z % zn) - zn * zb / 2};
                    generateCubes(sh, position, dimensions, current_pos);
                    current_pos += per_vertex;
                }
            }
        }

        np::dtype dt = np::dtype::get_builtin<double>();
        p::tuple shape = p::make_tuple(xn * yn * zn * per_vertex);
        p::tuple stride = p::make_tuple(sizeof(double));
        return np::from_data(sh,
                             dt,
                             shape,
                             stride,
                             p::object());
    }
    void getHeader(std::string filepath)
    {
        std::ifstream miffile;
        miffile.open(filepath, std::ios::out | std::ios_base::binary);
        std::string line;
        int buffer_size = 0;

        std::string node_reg("# xnodes:");
        std::string base_reg("# xbase:");

        if (miffile.is_open())
        {
            while (std::getline(miffile, line))
            {
                if (line.at(0) == '#')
                {
                    if (line == "# Begin: Data Binary 8")
                    {
                        buffer_size = 8;
                        break;
                    }
                    else if (line == "# Begin: Data Binary 4")
                    {
                        buffer_size = 4;
                    }

                    if (checkNodes && line.substr(0, node_reg.length()) == node_reg)
                    {

                        if (node_reg.at(2) == 'x')
                        {
                            xnodes = std::stoi(line.substr(node_reg.length(), line.length()));
                            node_reg.at(2) = 'y';
                        }
                        else if (node_reg.at(2) == 'y')
                        {
                            ynodes = std::stoi(line.substr(node_reg.length(), line.length()));
                            node_reg.at(2) = 'z';
                        }
                        else
                        {
                            znodes = std::stoi(line.substr(node_reg.length(), line.length()));
                            checkNodes = false;
                        }
                    }
                    if (checkBase && line.substr(0, base_reg.length()) == base_reg)
                    {

                        if (base_reg.at(2) == 'x')
                        {
                            xbase = std::stod(line.substr(base_reg.length(), line.length()));
                            base_reg.at(2) = 'y';
                        }
                        else if (base_reg.at(2) == 'y')
                        {
                            ybase = std::stod(line.substr(base_reg.length(), line.length()));
                            base_reg.at(2) = 'z';
                        }
                        else
                        {
                            zbase = std::stod(line.substr(base_reg.length(), line.length()));
                            checkBase = false;
                        }
                    }
                }
                else
                    break;
            }
            if (buffer_size <= 0)
            {
                throw "Invalid buffer size";
            }
            char IEEE_BUF[buffer_size];

            miffile.read(IEEE_BUF, buffer_size);

            double *IEEE_val = (double *)IEEE_BUF;
            if (IEEE_val[0] != 123456789012345.0)
            {
                throw "IEEE value not consistent";
            }
        }
        else
        {
            throw std::runtime_error("Invalid mif file");
        }
        if (buffer_size == 0)
        {
            miffile.close();
            throw std::runtime_error("Invalid mif file");
        }
        miffile.close();
    }

    np::ndarray getShapeAsNdarray(int xn, int yn, int zn, double xb, double yb, double zb)
    {
        double *sh = (double *)(malloc(sizeof(double) * xnodes * ynodes * znodes * 3));
        int current_pos = 0;
        int sampling = 1;
        for (int z = 0; z < zn; z += sampling)
        {
            for (int y = 0; y < yn; y += sampling)
            {
                for (int x = 0; x < xn; x += sampling)
                {
                    sh[current_pos + 0] = xb * (x % xn) - xn * xb / 2;
                    sh[current_pos + 1] = yb * (y % yn) - yn * yb / 2;
                    sh[current_pos + 2] = zb * (z % zn) - zn * zb / 2;
                    current_pos += 3;
                }
            }
        }
        np::dtype dt = np::dtype::get_builtin<double>();
        p::tuple shape = p::make_tuple(xn *
                                       yn *
                                       zn * 3);
        p::tuple stride = p::make_tuple(sizeof(double));
        return np::from_data(sh,
                             dt,
                             shape,
                             stride,
                             p::object());
    }

    np::ndarray getMifAsNdarrayWithColor(std::string path,
                                         int inflate,
                                         p::list color_vector_l,
                                         p::list positive_color_l,
                                         p::list negative_color_l)
    {
        double color_vector[3] = {
            p ::extract<double>(color_vector_l[0]),
            p ::extract<double>(color_vector_l[1]),
            p ::extract<double>(color_vector_l[2])};
        double positive_color[3] = {
            p ::extract<double>(positive_color_l[0]),
            p ::extract<double>(positive_color_l[1]),
            p ::extract<double>(positive_color_l[2])};

        double negative_color[3] = {
            p ::extract<double>(negative_color_l[0]),
            p ::extract<double>(negative_color_l[1]),
            p ::extract<double>(negative_color_l[2])};

        if (inflate < 0)
        {
            throw std::invalid_argument("Infalte cannot be 0 or less than 0");
        }

        std::ifstream miffile;
        miffile.open(path, std::ios::out | std::ios_base::binary);
        int buffer_size = getMifHeader(miffile);
        if (buffer_size == 0)
        {
            miffile.close();
            throw std::runtime_error("Invalid mif file");
        }

        int lines = znodes * xnodes * ynodes;
        char buffer[buffer_size * lines * 3];
        miffile.read(buffer, buffer_size * lines * 3);
        miffile.close();

        double *vals = (double *)buffer;
        double *fut_ndarray = (double *)(malloc(sizeof(double) * znodes * xnodes * ynodes * 3 * inflate));
        double mag, dot;
        double *array_to_cpy = (double *)(malloc(sizeof(double) * 3));
        int offset = 0;
        int sampling = 1;
        for (int i = 0; i < lines * 3; i += 3 * sampling)
        {
            mag = sqrt(pow(vals[i + 0], 2) + pow(vals[i + 1], 2) + pow(vals[i + 2], 2));
            if (mag == 0.0)
                mag = 1.0;
            dot = (vals[i + 0] / mag) * color_vector[0] +
                  (vals[i + 1] / mag) * color_vector[1] +
                  (vals[i + 2] / mag) * color_vector[2];

            if (dot > 0)
            {
                array_to_cpy[0] = positive_color[0] * dot + (1.0 - dot);
                array_to_cpy[1] = positive_color[1] * dot + (1.0 - dot);
                array_to_cpy[2] = positive_color[2] * dot + (1.0 - dot);
            }
            else
            {
                dot *= -1;

                array_to_cpy[0] = negative_color[0] * dot + (1.0 - dot);
                array_to_cpy[1] = negative_color[1] * dot + (1.0 - dot);
                array_to_cpy[2] = negative_color[2] * dot + (1.0 - dot);
            }
            for (int inf = 0; inf < inflate; inf++)
            {
                std::memcpy(fut_ndarray + offset, array_to_cpy, sizeof(double) * 3);
                offset += 3;
            }
        }

        np::dtype dt = np::dtype::get_builtin<double>();
        p::tuple shape = p::make_tuple(lines * 3 * inflate);
        p::tuple stride = p::make_tuple(sizeof(double));
        return np::from_data(fut_ndarray,
                             dt,
                             shape,
                             stride,
                             p::object());
    }

    np::ndarray getArrows(np::ndarray shape_outline,
                          np::ndarray vectors,
                          int resolution)
    {
        int inflate = 4 * resolution;

        double *fut_ndarray = (double *)(malloc(sizeof(double) * znodes * xnodes * ynodes * 3 * inflate));
        double pos[3], vec[3];
        int offset = 0;

        double theta = 2 * M_PI / resolution;
        double c = cos(theta);
        double s = sin(theta);
        double t_rotation[3][3] = {
            {c, -s, 0},
            {s, c, 0},
            {0, 0, 1}};

        int sampling = 1;
        for (int i = 0; i < xnodes * ynodes * znodes * 3; i += 3 * sampling)
        {
            pos[0] = p ::extract<double>(shape_outline[i + 0]);
            pos[1] = p ::extract<double>(shape_outline[i + 1]);
            pos[2] = p ::extract<double>(shape_outline[i + 2]);
            vec[0] = p ::extract<double>(vectors[i + 0]);
            vec[1] = p ::extract<double>(vectors[i + 1]);
            vec[2] = p ::extract<double>(vectors[i + 2]);
            generateVectors(fut_ndarray,
                            &offset,
                            pos,
                            vec,
                            t_rotation,
                            0.5,
                            0.5,
                            resolution);
        }
        np::dtype dt = np::dtype::get_builtin<double>();
        p::tuple shape = p::make_tuple(xnodes * ynodes * znodes * 3 * inflate);
        p::tuple stride = p::make_tuple(sizeof(double));
        return np::from_data(fut_ndarray,
                             dt,
                             shape,
                             stride,
                             p::object());
    }
};

BOOST_PYTHON_MODULE(AdvParser)
{
    // avoids the SIGSEV on dtype in numpy initialization
    boost::python::numpy::initialize();

    using namespace boost::python;

    class_<AdvParser>("AdvParser")
        .def(init<>())
        .def(init<AdvParser>())

        .def("getMifAsNdarrayWithColor", &AdvParser::getMifAsNdarrayWithColor)
        .def("getHeader", &AdvParser::getHeader)
        .def("getShapeAsNdarray", &AdvParser::getShapeAsNdarray)
        .def("getArrows", &AdvParser::getArrows)
        .def("generateIndices", &AdvParser::generateIndices)

        .add_property("xnodes", &AdvParser::getXnodes, &AdvParser::setXnodes)
        .add_property("ynodes", &AdvParser::getYnodes, &AdvParser::setYnodes)
        .add_property("znodes", &AdvParser::getZnodes, &AdvParser::setZnodes)

        .add_property("xbase", &AdvParser::getXbase, &AdvParser::setXbase)
        .add_property("ybase", &AdvParser::getYbase, &AdvParser::setYbase)
        .add_property("zbase", &AdvParser::getZbase, &AdvParser::setZbase);
}
