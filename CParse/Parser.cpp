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

struct VectorObj
{
    _Float32 x;
    _Float32 y;
    _Float32 z;
    _Float32 mag;

    VectorObj() : x(0.0), y(0.0), z(0.0), mag(0.0) {}
    VectorObj(_Float32 x, _Float32 y, _Float32 z)
    {
        VectorObj::mag = sqrt(pow(x, 2) + pow(y, 2) + pow(z, 2));
        if (mag != 0)
        {
            VectorObj::x = x / mag;
            VectorObj::y = y / mag;
            VectorObj::z = z / mag;
        }
    }

    void setX(_Float32 val) { this->x = val; }
    void setY(_Float32 val) { this->y = val; }
    void setZ(_Float32 val) { this->z = val; }
    void setMag(_Float32 val) { this->mag = val; }

    _Float32 getX() { return x; }
    _Float32 getY() { return y; }
    _Float32 getZ() { return z; }
    _Float32 getMag() { return mag; }

    bool operator==(VectorObj const &val) const
    {
        return (x == val.x) && (y == val.y) && (z == val.z);
    }
    bool operator!=(VectorObj const &val) const
    {
        return (x != val.x) || (y != val.y) || (z != val.z);
    }

    std::string repr() const
    {
        return std::to_string(x) + " " + std::to_string(y) + " " + std::to_string(z);
    }
};

struct Parser
{
    std::vector<std::vector<VectorObj>> fileList;
    bool checkBase = true;
    bool checkNodes = true;
    int xnodes, ynodes, znodes;
    double xbase, ybase, zbase;
    std::string def_ext;

    Parser()
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

    std::vector<std::vector<VectorObj>> getVectors()
    {
        return fileList;
    }

    int listFiles(std::string dirpath)
    {
        if (!fs::exists(dirpath))
        {
            std::cout << "\nNot found: " << dirpath << std::endl;
            return 1;
        }
        if (fs::is_directory(dirpath))
        {
            fs::directory_iterator end_iter;
            for (fs::directory_iterator dir_it(dirpath); dir_it != end_iter; dir_it++)
            {
                if (fs::is_regular_file(dir_it->status()) && dir_it->path().extension() == this->def_ext)
                {
                    std::cout << dir_it->path().string() << std::endl;
                }
            }
        }
        else
        {
            std::cout << "\nNot a directory: " << dirpath << std::endl;
        }
        return 0;
    }

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

    std::vector<VectorObj> getMifAsVectorObj(std::string path)
    {
        std::vector<VectorObj> vectors;
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
        double *vals = (double *)buffer;

        for (int i = 0; i < lines; i += 3)
        {
            vectors.push_back(VectorObj(vals[i + 0], vals[i + 1], vals[i + 2]));
        }

        miffile.close();
        return vectors;
    }

    std::vector<std::vector<double>> getMifAsDblObj(std::string path)
    {
        std::vector<std::vector<double>> vectors;

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
        double *vals = (double *)buffer;
        for (int i = 0; i < lines * 3; i += 3)
        {
            std::vector<double> tmp = {vals[i + 0], vals[i + 1], vals[i + 2]};
            vectors.push_back(tmp);
        }

        miffile.close();
        return vectors;
    }

    void getArrowVectors(double *vbo, 
                                double pos[3],
                                double col[3],
                                int resolution,
                                int height,
                                int radius,
                                int offset){
        for (int i = 0; i < resolution -1; i++){
            vbo[*offset + i + 0] = math.sin(
        }
    }

    np::ndarray getMifAsNdarray(std::string path)
    {

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
        double *vals = (double *)buffer;
        double *fut_ndarray = (double *)(malloc(sizeof(double) * lines * 3));
        double mag;
        for (int i = 0; i < lines * 3; i += 3)
        {
            mag = sqrt(pow(vals[i + 0], 2) + pow(vals[i + 1], 2) + pow(vals[i + 2], 2));
            if (mag == 0.0)
                mag = 1.0;
            fut_ndarray[i + 0] = vals[i + 0] / mag;
            fut_ndarray[i + 1] = vals[i + 1] / mag;
            fut_ndarray[i + 2] = vals[i + 2] / mag;
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
        miffile.close();
        return vectorData;
    }
};

BOOST_PYTHON_MODULE(Parser)
{
    // avoids the SIGSEV on dtype in numpy initialization
    boost::python::numpy::initialize();

    using namespace boost::python;

    class_<VectorObj>("VectorObj", init<double, double, double>())
        .def("__repr__", &VectorObj::repr)
        .add_property("x", &VectorObj::getX, &VectorObj::setX)
        .add_property("y", &VectorObj::getY, &VectorObj::setY)
        .add_property("z", &VectorObj::getZ, &VectorObj::setZ)
        .add_property("mag", &VectorObj::getMag, &VectorObj::setMag);

    class_<std::vector<VectorObj>>("MifObj")
        .def(vector_indexing_suite<std::vector<VectorObj>>());

    class_<std::vector<double>>("DblObj")
        .def(vector_indexing_suite<std::vector<double>>());

    class_<std::vector<std::vector<double>>>("VecDblObj")
        .def(vector_indexing_suite<std::vector<std::vector<double>>>());

    class_<Parser>("Parser")
        .def(init<>())
        .def(init<Parser>())
        .def("getMifAsVectorObj", &Parser::getMifAsVectorObj)
        .def("getMifAsDblObj", &Parser::getMifAsDblObj)
        .def("getMifAsNdarray", &Parser::getMifAsNdarray)
        .def("getFileList", &Parser::listFiles)

        .add_property("xnodes", &Parser::getXnodes, &Parser::setXnodes)
        .add_property("ynodes", &Parser::getYnodes, &Parser::setYnodes)
        .add_property("znodes", &Parser::getZnodes, &Parser::setZnodes)

        .add_property("xbase", &Parser::getXbase, &Parser::setXbase)
        .add_property("ybase", &Parser::getYbase, &Parser::setYbase)
        .add_property("zbase", &Parser::getZbase, &Parser::setZbase);
}
