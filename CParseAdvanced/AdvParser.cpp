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

    void generateCubes(double *shape_outline, double position[3], double dimensions[3], int current_pos)
    {
        double arr[96] = {
            //TOP FACE
            position[0] + dimensions[0], position[1], position[2] + dimensions[2], position[3],
            position[0], position[1], position[2] + dimensions[2], position[3],
            position[0], position[1] + dimensions[1], position[2] + dimensions[2], position[3],
            position[0] + dimensions[0], position[1] + dimensions[1], position[2] + dimensions[2], position[3],
            //BOTTOM FACE
            position[0] + dimensions[0], position[1], position[2], position[3],
            position[0], position[1], position[2], position[3],
            position[0], position[1] + dimensions[1], position[2], position[3],
            position[0] + dimensions[0], position[1] + dimensions[1], position[2], position[3],
            //FRONT FACE
            position[0] + dimensions[0], position[1] + dimensions[1], position[2] + dimensions[2], position[3],
            position[0], position[1] + dimensions[1], position[2] + dimensions[2], position[3],
            position[0], position[1] + dimensions[1], position[2], position[3],
            position[0] + dimensions[0], position[1] + dimensions[1], position[2], position[3],
            //BACK FACE
            position[0] + dimensions[0], position[1], position[2] + dimensions[2], position[3],
            position[0], position[1], position[2] + dimensions[2], position[3],
            position[0], position[1], position[2], position[3],
            position[0] + dimensions[0], position[1], position[2], position[3],
            //RIGHT FACE
            position[0] + dimensions[0], position[1], position[2] + dimensions[2], position[3],
            position[0] + dimensions[0], position[1] + dimensions[1], position[2] + dimensions[2], position[3],
            position[0] + dimensions[0], position[1] + dimensions[1], position[2], position[3],
            position[0] + dimensions[0], position[1], position[2], position[3],
            //LEFT FACE
            position[0], position[1] + dimensions[1], position[2] + dimensions[2], position[3],
            position[0], position[1], position[2] + dimensions[2], position[3],
            position[0], position[1], position[2], position[3],
            position[0], position[1] + dimensions[1], position[2], position[3]};
        std::memcpy(shape_outline + current_pos, arr, sizeof(double) * 96);
        // std::copy(std::begin(arr), std::end(src), shape_outline);
    }

    np::ndarray getShapeOutline(int xn, int yn, int zn, double xb, double yb, double zb, int per_vertex)
    {
        double *shape_outline = (double *)(malloc(sizeof(double) * xn * yn * zn * per_vertex));
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
                    std::memcpy(shape_outline + current_pos, arr, sizeof(double) * 72);
                    current_pos += per_vertex;
                }
            }
        }

        np::dtype dt = np::dtype::get_builtin<double>();
        p::tuple shape = p::make_tuple(xn * yn * zn * per_vertex);
        p::tuple stride = p::make_tuple(sizeof(double));
        return np::from_data(shape_outline,
                             dt,
                             shape,
                             stride,
                             p::object());
    }

    np::ndarray getMifAsNdarrayWithColor(std::string path,
                                         int inflate,
                                         p::list color_vector_l,
                                         p::list positive_color_l, p::list negative_color_l)
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
        for (int i = 0; i < lines * 3; i += 3)
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

                // fut_ndarray[i + 0 + inf + inflate * (int)(i / 3)] = positive_color[0] * dot + (1.0 - dot);
                // fut_ndarray[i + 1 + inf + inflate * (int)(i / 3)] = positive_color[1] * dot + (1.0 - dot);
                // fut_ndarray[i + 2 + inf + inflate * (int)(i / 3)] = positive_color[2] * dot + (1.0 - dot);
            }
            else
            {
                dot *= -1;

                array_to_cpy[0] = negative_color[0] * dot + (1.0 - dot);
                array_to_cpy[1] = negative_color[1] * dot + (1.0 - dot);
                array_to_cpy[2] = negative_color[2] * dot + (1.0 - dot);

                // fut_ndarray[i + 0 + inf + inflate * (int)(i / 3)] = negative_color[0] * dot + (1.0 - dot);
                // fut_ndarray[i + 1 + inf + inflate * (int)(i / 3)] = negative_color[1] * dot + (1.0 - dot);
                // fut_ndarray[i + 2 + inf + inflate * (int)(i / 3)] = negative_color[2] * dot + (1.0 - dot);
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
        .def("getShapeOutline", &AdvParser::getShapeOutline)

        .add_property("xnodes", &AdvParser::getXnodes, &AdvParser::setXnodes)
        .add_property("ynodes", &AdvParser::getYnodes, &AdvParser::setYnodes)
        .add_property("znodes", &AdvParser::getZnodes, &AdvParser::setZnodes)

        .add_property("xbase", &AdvParser::getXbase, &AdvParser::setXbase)
        .add_property("ybase", &AdvParser::getYbase, &AdvParser::setYbase)
        .add_property("zbase", &AdvParser::getZbase, &AdvParser::setZbase);
}
