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

#include <boost/python/suite/indexing/vector_indexing_suite.hpp>
#include <boost/python/module.hpp>
#include <boost/python/def.hpp>
#include <boost/python/implicit.hpp>

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
    bool check = true;
    int xnodes, ynodes, znodes;

    Parser()
    {
        xnodes = 0;
        ynodes = 0;
        znodes = 0;
    };

    void setX(int val) { this->xnodes = val; }
    void setY(int val) { this->ynodes = val; }
    void setZ(int val) { this->znodes = val; }
    int getXnodes() { return xnodes; }
    int getYnodes() { return ynodes; }
    int getZnodes() { return znodes; }

    std::vector<std::vector<VectorObj>> getVectors()
    {
        return fileList;
    }

    void listFiles(std::string dirpath)
    {

        for (auto &i : std::filesystem::directory_iterator(dirpath))
        {
            if (i.is_regular_file() && i.path().extension() == ".omf")
            {
                fileList.push_back(parseMifFile(i.path()));
                std::cout << i << std::endl;
            }
        }
    }
    std::vector<VectorObj> parseMifFile(std::string path)
    {
        std::vector<VectorObj> vectors;
        std::string line;
        int buffer_size = 0;
        int how_many_lines;
        std::ifstream miffile(path, std::ios::out | std::ios_base::binary);

        std::string reg_string("# xnodes:");
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

                    if (check && line.substr(0, reg_string.length()) == reg_string)
                    {

                        if (reg_string.at(2) == 'x')
                        {
                            xnodes = std::stoi(line.substr(reg_string.length(), line.length()));
                            reg_string.at(2) = 'y';
                        }
                        else if (reg_string.at(2) == 'y')
                        {
                            ynodes = std::stoi(line.substr(reg_string.length(), line.length()));
                            reg_string.at(2) = 'z';
                        }
                        else
                        {
                            znodes = std::stoi(line.substr(reg_string.length(), line.length()));
                            check = false;
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

            int lines = znodes * xnodes * ynodes;
            char buffer[buffer_size * lines * 3];
            miffile.read(buffer, buffer_size * lines * 3);
            double *vals = (double *)buffer;

            for (int i = 0; i < lines; i += 3)
            {
                vectors.push_back(VectorObj(vals[i + 0], vals[i + 1], vals[i + 2]));
            }

            miffile.close();
        }
        return vectors;
    }

    std::vector<std::vector<double>> parseMifFile2(std::string path)
    {
        std::vector<std::vector<double>> vectors;
        std::string line;
        int buffer_size = 0;
        int how_many_lines;
        std::ifstream miffile(path, std::ios::out | std::ios_base::binary);

        std::string reg_string("# xnodes:");
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
                        break;
                    }
                    if (check && line.substr(0, reg_string.length()) == reg_string)
                    {

                        if (reg_string.at(2) == 'x')
                        {
                            xnodes = std::stoi(line.substr(reg_string.length(), line.length()));
                            reg_string.at(2) = 'y';
                        }
                        else if (reg_string.at(2) == 'y')
                        {
                            ynodes = std::stoi(line.substr(reg_string.length(), line.length()));
                            reg_string.at(2) = 'z';
                        }
                        else
                        {
                            znodes = std::stoi(line.substr(reg_string.length(), line.length()));
                            check = false;
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

            int lines = znodes * xnodes * ynodes;
            char buffer[buffer_size * lines * 3];
            miffile.read(buffer, buffer_size * lines * 3);
            double *vals = (double *)buffer;
            for (int i = 0; i < lines * 3; i += 3)
            {
                std::vector<double> tmp = {vals[i + 0], vals[i + 1], vals[i + 2]};
                vectors.push_back(tmp);
                // vectors.insert(vector.end(),
                //                {vals[i + 0], vals[i + 1], vals[i + 2]});
            }

            miffile.close();
        }
        return vectors;
    }
};

BOOST_PYTHON_MODULE(Parser)
{
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
        .def("parseMif", &Parser::parseMifFile)
        .def("getMif", &Parser::parseMifFile2)
        .add_property("xnodes", &Parser::getXnodes, &Parser::setX)
        .add_property("ynodes", &Parser::getYnodes, &Parser::setY)
        .add_property("znodes", &Parser::getZnodes, &Parser::setZ);
}
