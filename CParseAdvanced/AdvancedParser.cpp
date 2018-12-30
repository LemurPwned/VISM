#include <iostream>
#include <stdio.h>
#include <vector>
#include <cmath>
#include <fstream>
#include <string>
#include <regex>
#include <iterator>
#include <filesystem>
#include <python3.7m/Python.h>
#include <boost/python.hpp>
#include <boost/python/numpy.hpp>

#include <boost/python/suite/indexing/vector_indexing_suite.hpp>
#include <boost/python/module.hpp>
#include <boost/python/def.hpp>
#include <boost/python/implicit.hpp>

#include "boost/filesystem.hpp"
#include "boost/filesystem/operations.hpp"
#include "boost/filesystem/path.hpp"

namespace fs = boost::filesystem;
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

    int *generateCubes(int position[3], int dimensions[3])
    {
        return {
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
    }

    np::ndarray getShapeOutline(int xn, int yn, int zn, int xb, int yb, int zb, int per_vertex)
    {
        double *shape = (double *)(malloc(sizeof(double) * xn * yn * zn * per_vertex));
        // double *outline = (double *)(malloc(sizeof(double) * xn * yn * zn * 3));
        int pos[3];
        int dims[3] = {1.0, 1.0, 1.0};
        for (int z = 0; z < zc; z++)
        {
            for (int y = 0; y < yc; y++)
            {
                for (int k = 0; k < xc; k++)
                {
                    int pos[] = {xb * (x % xn), yb * (y % yn), zb * (z % zn)};
                    (double *shape) = (double *)generateCubes(pos, dims);
                    shape += per_vertex;
                    // outline[x + y + z + 0] = xb * (x % xn);
                    // outline[x + y + z + 1] = yb * (y % yn);
                    // outline[x + y + z + 2] = zb * (z % zn);
                }
            }
        }

        // np::dtype dt = np::dtype::get_builtin<double>();
        // p::tuple shape = p::make_tuple(xn * yn * zn, 3);
        // p::tuple stride = p::make_tuple(3 * sizeof(double), sizeof(double));
        // return np::from_data(outline,
        //                      dt,
        //                      shape,
        //                      stride,
        //                      p::object());
    }

    np::ndarray getMifAsNdarrayWithColor(std::string path,
                                         int inflate,
                                         double color_vector[3],
                                         double positive_color[3], double negative_color[3])
    {

        if (inflate < 0)
        {
            throw std::argument_error("Infalte cannot be 0 or less than 0");
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
        double *fut_ndarray = (double *)(malloc(sizeof(double) * lines * 3 * inflate));
        double mag, dot;
        for (int i = 0; i < lines * 3; i += 3)
        {
            mag = sqrt(pow(vals[i + 0], 2) + pow(vals[i + 1], 2) + pow(vals[i + 2], 2));
            if (mag == 0.0)
                mag = 1.0;
            dot = (vals[i + 0] / mag) * color_vector[0] +
                  (vals[i + 1] / mag) * color_vector[1] +
                  (vals[i + 2] / mag) * color_vector[2];
            for (int inf = 0; inf < inflate; inf++)
            {
                if (dot > 0)
                {
                    fut_ndarray[i + 0 + inf] = positive_color[0] * dot + (1.0 - dot);
                    fut_ndarray[i + 1 + inf] = positive_color[1] * dot + (1.0 - dot);
                    fut_ndarray[i + 2 + inf] = positive_color[2] * dot + (1.0 - dot);
                }
                else
                {
                    dot *= 1;
                    fut_ndarray[i + 0 + inf] = negative_color[0] * dot + (1.0 - dot);
                    fut_ndarray[i + 1 + inf] = negative_color[1] * dot + (1.0 - dot);
                    fut_ndarray[i + 2 + inf] = negative_color[2] * dot + (1.0 - dot);
                }
            }
        }

        // use explicit namespace here to make sure it does not mix the functions
        boost::python::numpy::dtype dt1 = boost::python::numpy::dtype::get_builtin<double>();
        boost::python::tuple shape = boost::python::make_tuple(lines, 3);
        boost::python::tuple stride = boost::python::make_tuple(3 * sizeof(double), sizeof(double));
        boost::python::numpy::ndarray vectorData = boost::python::numpy::from_data(fut_ndarray,
                                                                                   dt1,
                                                                                   shape,
                                                                                   stride,
                                                                                   boost::python::object());
        // last entry is object owner
        return vectorData;
    }
};

BOOST_PYTHON_MODULE(AdvParser)
{
    // avoids the SIGSEV on dtype in numpy initialization
    boost::python::numpy::initialize();

    using namespace boost::python;

    class_<Parser>("AdvParser")
        .def(init<>())
        .def(init<Parser>())

        .def("getMifAsNdarrayWithColor", &Parser::getMifAsNdarrayWithColor)
        .def("getShapeOutline", &Parser::getShapeOutline)

        .add_property("xnodes", &Parser::getXnodes, &Parser::setXnodes)
        .add_property("ynodes", &Parser::getYnodes, &Parser::setYnodes)
        .add_property("znodes", &Parser::getZnodes, &Parser::setZnodes)

        .add_property("xbase", &Parser::getXbase, &Parser::setXbase)
        .add_property("ybase", &Parser::getYbase, &Parser::setYbase)
        .add_property("zbase", &Parser::getZbase, &Parser::setZbase);
}
