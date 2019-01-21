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
#include <arpa/inet.h>
#include <netinet/in.h>

namespace p = boost::python;
namespace np = boost::python::numpy;

struct AdvParser
{
    bool checkBase = true;
    bool checkNodes = true;
    bool shapeCreated = true;
    int xnodes, ynodes, znodes;
    double xbase, ybase, zbase;
    AdvParser()
    {
        xnodes = 0;
        ynodes = 0;
        znodes = 0;

        xbase = 0.0;
        ybase = 0.0;
        zbase = 0.0;
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
                        break;
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
                throw std::runtime_error("Invalid buffer size");
            }
            char IEEE_BUF[buffer_size + 1];

            miffile.read(IEEE_BUF, buffer_size);
            if (buffer_size == 4)
            {
                float IEEE_val;
                float IEEE_VALIDATION = 1234567.0;

                std::memcpy(&IEEE_val, IEEE_BUF, sizeof(float));
                if (IEEE_val != IEEE_VALIDATION)
                {
                    printf("%f\n", IEEE_val);
                    throw std::runtime_error("IEEE value not consistent");
                }
            }
            else if (buffer_size == 8)
            {
                double IEEE_val;
                double IEEE_VALIDATION = 123456789012345.0;
                std::memcpy(&IEEE_val, IEEE_BUF, sizeof(double));

                if (IEEE_val != IEEE_VALIDATION)
                {
                    printf("%f\n", IEEE_val);
                    throw std::runtime_error("IEEE value not consistent");
                }
            }
            else
            {
                throw std::runtime_error("Unspecified or invalid buffer size for binary input data");
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

    void a_cross_b(double a[3], double b[3], double c[3])
    {
        c[0] = a[1] * b[2] - a[2] * b[1];
        c[1] = a[2] * b[0] - a[0] * b[2];
        c[2] = a[0] * b[1] - a[1] * b[0];
    }
    void generateVectors2(double *vbo,
                          int *offset,
                          int *normal_offset,
                          double position[3],
                          double vector[3], // from omf
                          double t_rotation[3][3],
                          double height,
                          double radius,
                          int resolution)
    {
        double height_operator[3] = {0, 0, height * 1.5};
        double mag = sqrt(pow(vector[0], 2) +
                          pow(vector[1], 2) +
                          pow(vector[2], 2));
        double phi = acos(vector[2] / mag);         // z rot
        double theta = atan2(vector[1], vector[0]); // y rot
        double ct = cos(theta);
        double st = sin(theta);
        double cp = cos(phi);
        double sp = sin(phi);
        double rotation_matrix[3][3] = {
            {ct, -st * cp, st * sp},
            {st, cp * ct, -sp * ct},
            {0, sp, cp}};
        double origin_base[3], cpy[3];
        double cyllinder_co_rot[3] = {radius, radius, 0};
        double cone_co_rot[3] = {2 * radius, 2 * radius, 0};
        std::memcpy(origin_base, position, sizeof(double) * 3);
        double n[3], u[3], v[3];

        for (int i = 0; i < (resolution - 1); i++)
        {
            // bottom triangle - cyllinder
            matrix_vector_cpy(rotation_matrix, cyllinder_co_rot, cpy);
            vbo[*offset] = 1;
            vbo[*offset + 0] = origin_base[0] + cpy[0];
            vbo[*offset + 1] = origin_base[1] + cpy[1];
            vbo[*offset + 2] = origin_base[2] + cpy[2];

            // bottom triangle - cone
            cone_co_rot[2] += height;
            matrix_vector_cpy(rotation_matrix, cone_co_rot, cpy);
            vbo[*offset + 3] = origin_base[0] + cpy[0];
            vbo[*offset + 4] = origin_base[1] + cpy[1];
            vbo[*offset + 5] = origin_base[2] + cpy[2];

            // top triangle - cyllinder
            cyllinder_co_rot[2] += height;
            matrix_vector_cpy(rotation_matrix, cyllinder_co_rot, cpy);
            vbo[*offset + 12] = origin_base[0] + cpy[0];
            vbo[*offset + 13] = origin_base[1] + cpy[1];
            vbo[*offset + 14] = origin_base[2] + cpy[2];

            // top triangle - cone
            matrix_vector_mul(rotation_matrix, height_operator);
            vbo[*offset + 15] = origin_base[0] + height_operator[0];
            vbo[*offset + 16] = origin_base[1] + height_operator[1];
            vbo[*offset + 17] = origin_base[2] + height_operator[2];
            height_operator[0] = 0;
            height_operator[1] = 0;
            height_operator[2] = 1.5 * height;
            cyllinder_co_rot[2] -= height;
            cone_co_rot[2] -= height;

            matrix_vector_mul(t_rotation, cyllinder_co_rot);
            matrix_vector_mul(t_rotation, cone_co_rot);

            if (i > 0)
            {
                // firstly compute the later indices for vertex
                // because we will use them to compute the normals

                // normals to the cyllinder triangle
                u[0] = vbo[*offset + 0] - vbo[*offset - 24 + 12];
                u[1] = vbo[*offset + 1] - vbo[*offset - 24 + 13];
                u[2] = vbo[*offset + 2] - vbo[*offset - 24 + 14];

                v[0] = vbo[*offset + 12] - vbo[*offset - 24 + 12];
                v[1] = vbo[*offset + 13] - vbo[*offset - 24 + 13];
                v[2] = vbo[*offset + 14] - vbo[*offset - 24 + 14];

                // cross product
                a_cross_b(u, v, n);
                vbo[*normal_offset + 0] = n[0];
                vbo[*normal_offset + 1] = n[1];
                vbo[*normal_offset + 2] = n[2];

                // normals to the cone triangle
                u[0] = vbo[*offset + 3] - vbo[*offset - 24 + 15];
                u[1] = vbo[*offset + 4] - vbo[*offset - 24 + 16];
                u[2] = vbo[*offset + 5] - vbo[*offset - 24 + 17];

                v[0] = vbo[*offset + 15] - vbo[*offset - 24 + 15];
                v[1] = vbo[*offset + 16] - vbo[*offset - 24 + 16];
                v[2] = vbo[*offset + 17] - vbo[*offset - 24 + 17];

                // cross product
                a_cross_b(u, v, n);
                vbo[*normal_offset + 3] = n[0];
                vbo[*normal_offset + 4] = n[1];
                vbo[*normal_offset + 5] = n[2];
                *normal_offset += 12;
            }
            *offset += 24;
        }
        // reset rotational vectors to their defaults
        cyllinder_co_rot[0] = radius;
        cyllinder_co_rot[1] = radius;
        cyllinder_co_rot[2] = 0;
        matrix_vector_mul(rotation_matrix, cyllinder_co_rot);
        vbo[*offset + 0] = origin_base[0] + cyllinder_co_rot[0];
        vbo[*offset + 1] = origin_base[1] + cyllinder_co_rot[1];
        vbo[*offset + 2] = origin_base[2] + cyllinder_co_rot[2];

        cone_co_rot[0] = 2 * radius;
        cone_co_rot[1] = 2 * radius;
        cone_co_rot[2] = height;
        matrix_vector_mul(rotation_matrix, cone_co_rot);
        vbo[*offset + 3] = origin_base[0] + cone_co_rot[0];
        vbo[*offset + 4] = origin_base[1] + cone_co_rot[1];
        vbo[*offset + 5] = origin_base[2] + cone_co_rot[2];

        cyllinder_co_rot[0] = radius;
        cyllinder_co_rot[1] = radius;
        cyllinder_co_rot[2] += height;
        matrix_vector_mul(rotation_matrix, cyllinder_co_rot);
        vbo[*offset + 12] = origin_base[0] + cyllinder_co_rot[0];
        vbo[*offset + 13] = origin_base[1] + cyllinder_co_rot[1];
        vbo[*offset + 14] = origin_base[2] + cyllinder_co_rot[2];

        height_operator[0] = 0;
        height_operator[1] = 0;
        height_operator[2] = 1.5 * height;
        matrix_vector_mul(rotation_matrix, height_operator);
        vbo[*offset + 15] = origin_base[0] + height_operator[0];
        vbo[*offset + 16] = origin_base[1] + height_operator[1];
        vbo[*offset + 17] = origin_base[2] + height_operator[2];

        // normals to the cyllinder triangle
        u[0] = vbo[*offset + 0] - vbo[*offset - 24 + 12];
        u[1] = vbo[*offset + 1] - vbo[*offset - 24 + 13];
        u[2] = vbo[*offset + 2] - vbo[*offset - 24 + 14];

        v[0] = vbo[*offset + 12] - vbo[*offset - 24 + 12];
        v[1] = vbo[*offset + 13] - vbo[*offset - 24 + 13];
        v[2] = vbo[*offset + 14] - vbo[*offset - 24 + 14];

        // cross product
        a_cross_b(u, v, n);
        vbo[*normal_offset + 0] = n[0];
        vbo[*normal_offset + 1] = n[1];
        vbo[*normal_offset + 2] = n[2];

        // normals to the cone triangle
        u[0] = vbo[*offset + 3] - vbo[*offset - 24 + 15];
        u[1] = vbo[*offset + 4] - vbo[*offset - 24 + 16];
        u[2] = vbo[*offset + 5] - vbo[*offset - 24 + 17];

        v[0] = vbo[*offset + 15] - vbo[*offset - 24 + 15];
        v[1] = vbo[*offset + 16] - vbo[*offset - 24 + 16];
        v[2] = vbo[*offset + 17] - vbo[*offset - 24 + 17];

        // cross product
        a_cross_b(u, v, n);
        vbo[*normal_offset + 3] = n[0];
        vbo[*normal_offset + 4] = n[1];
        vbo[*normal_offset + 5] = n[2];
        *offset += 24;
        *normal_offset += 12;
    }

    void generateVBO(double *vbo,
                     int *offset,
                     int *normal_offset,
                     double position[3],
                     double vector[3], // from omf
                     double color[3],  // from omf
                     double t_rotation[3][3],
                     double height,
                     double radius,
                     int resolution)
    {
        double height_operator[3] = {0, 0, height * 1.5};
        double mag = sqrt(pow(vector[0], 2) +
                          pow(vector[1], 2) +
                          pow(vector[2], 2));
        double phi = acos(vector[2] / mag);         // z rot
        double theta = atan2(vector[1], vector[0]); // y rot
        double ct = cos(theta);
        double st = sin(theta);
        double cp = cos(phi);
        double sp = sin(phi);
        double rotation_matrix[3][3] = {
            {ct, -st * cp, st * sp},
            {st, cp * ct, -sp * ct},
            {0, sp, cp}};
        double origin_base[3], cpy[3];
        double cyllinder_co_rot[3] = {radius, radius, 0};
        double cone_co_rot[3] = {2 * radius, 2 * radius, 0};
        std::memcpy(origin_base, position, sizeof(double) * 3);
        double n[3], u[3], v[3];
        int prev_off = 36;
        for (int i = 0; i < (resolution - 1); i++)
        {
            // colors first
            std::memcpy(vbo + *offset, color, sizeof(double) * 3);
            std::memcpy(vbo + *offset + 9, color, sizeof(double) * 3);
            std::memcpy(vbo + *offset + 18, color, sizeof(double) * 3);
            std::memcpy(vbo + *offset + 27, color, sizeof(double) * 3);
            // bottom triangle - cyllinder
            matrix_vector_cpy(rotation_matrix, cyllinder_co_rot, cpy);
            vbo[*offset + 3] = origin_base[0] + cpy[0];
            vbo[*offset + 4] = origin_base[1] + cpy[1];
            vbo[*offset + 5] = origin_base[2] + cpy[2];

            // bottom triangle - cone
            cone_co_rot[2] += height;
            matrix_vector_cpy(rotation_matrix, cone_co_rot, cpy);
            vbo[*offset + 6] = origin_base[0] + cpy[0];
            vbo[*offset + 7] = origin_base[1] + cpy[1];
            vbo[*offset + 8] = origin_base[2] + cpy[2];

            // top triangle - cyllinder
            cyllinder_co_rot[2] += height;
            matrix_vector_cpy(rotation_matrix, cyllinder_co_rot, cpy);
            vbo[*offset + 21] = origin_base[0] + cpy[0];
            vbo[*offset + 22] = origin_base[1] + cpy[1];
            vbo[*offset + 23] = origin_base[2] + cpy[2];

            // top triangle - cone
            matrix_vector_mul(rotation_matrix, height_operator);
            vbo[*offset + 24] = origin_base[0] + height_operator[0];
            vbo[*offset + 25] = origin_base[1] + height_operator[1];
            vbo[*offset + 26] = origin_base[2] + height_operator[2];
            height_operator[0] = 0;
            height_operator[1] = 0;
            height_operator[2] = 1.5 * height;
            cyllinder_co_rot[2] -= height;
            cone_co_rot[2] -= height;

            matrix_vector_mul(t_rotation, cyllinder_co_rot);
            matrix_vector_mul(t_rotation, cone_co_rot);

            if (i > 0)
            {
                // firstly compute the later indices for vertex
                // because we will use them to compute the normals

                u[0] = vbo[*offset + 3] - vbo[*offset - prev_off + 3];
                u[1] = vbo[*offset + 4] - vbo[*offset - prev_off + 4];
                u[2] = vbo[*offset + 5] - vbo[*offset - prev_off + 5];

                v[0] = vbo[*offset - prev_off + 21] + vbo[*offset - prev_off + 3];
                v[1] = vbo[*offset - prev_off + 22] + vbo[*offset - prev_off + 4];
                v[2] = vbo[*offset - prev_off + 23] + vbo[*offset - prev_off + 5];

                // cross product
                a_cross_b(u, v, n);
                vbo[*normal_offset + 0] = n[0];
                vbo[*normal_offset + 1] = n[1];
                vbo[*normal_offset + 2] = n[2];

                // normals to the cone triangle
                u[0] = vbo[*offset + 6] - vbo[*offset - prev_off + 6];
                u[1] = vbo[*offset + 7] - vbo[*offset - prev_off + 7];
                u[2] = vbo[*offset + 8] - vbo[*offset - prev_off + 8];

                v[0] = vbo[*offset - prev_off + 24] - vbo[*offset - prev_off + 6];
                v[1] = vbo[*offset - prev_off + 25] - vbo[*offset - prev_off + 7];
                v[2] = vbo[*offset - prev_off + 26] - vbo[*offset - prev_off + 8];

                // cross product
                a_cross_b(u, v, n);
                vbo[*normal_offset + 3] = n[0];
                vbo[*normal_offset + 4] = n[1];
                vbo[*normal_offset + 5] = n[2];
                *normal_offset += 18;

                // normals to the cyllinder triangle
                u[0] = vbo[*offset + 3] - vbo[*offset - prev_off + 21];
                u[1] = vbo[*offset + 4] - vbo[*offset - prev_off + 22];
                u[2] = vbo[*offset + 5] - vbo[*offset - prev_off + 23];

                v[0] = vbo[*offset + 21] - vbo[*offset - prev_off + 21];
                v[1] = vbo[*offset + 22] - vbo[*offset - prev_off + 22];
                v[2] = vbo[*offset + 23] - vbo[*offset - prev_off + 23];

                // cross product
                a_cross_b(u, v, n);
                vbo[*normal_offset + 0] = n[0];
                vbo[*normal_offset + 1] = n[1];
                vbo[*normal_offset + 2] = n[2];

                // normals to the cone triangle
                u[0] = vbo[*offset + 6] - vbo[*offset - prev_off + 24];
                u[1] = vbo[*offset + 7] - vbo[*offset - prev_off + 25];
                u[2] = vbo[*offset + 8] - vbo[*offset - prev_off + 26];

                v[0] = vbo[*offset + 24] - vbo[*offset - prev_off + 24];
                v[1] = vbo[*offset + 25] - vbo[*offset - prev_off + 25];
                v[2] = vbo[*offset + 26] - vbo[*offset - prev_off + 26];

                // cross product
                a_cross_b(u, v, n);
                vbo[*normal_offset + 3] = n[0];
                vbo[*normal_offset + 4] = n[1];
                vbo[*normal_offset + 5] = n[2];
                *normal_offset += 18;
            }
            *offset += prev_off;
        }
        // colors first
        std::memcpy(vbo + *offset, color, sizeof(double) * 3);
        std::memcpy(vbo + *offset + 9, color, sizeof(double) * 3);
        std::memcpy(vbo + *offset + 18, color, sizeof(double) * 3);
        std::memcpy(vbo + *offset + 27, color, sizeof(double) * 3);
        // reset rotational vectors to their defaults
        cyllinder_co_rot[0] = radius;
        cyllinder_co_rot[1] = radius;
        cyllinder_co_rot[2] = 0;
        matrix_vector_mul(rotation_matrix, cyllinder_co_rot);
        vbo[*offset + 3] = origin_base[0] + cyllinder_co_rot[0];
        vbo[*offset + 4] = origin_base[1] + cyllinder_co_rot[1];
        vbo[*offset + 5] = origin_base[2] + cyllinder_co_rot[2];

        cone_co_rot[0] = 2 * radius;
        cone_co_rot[1] = 2 * radius;
        cone_co_rot[2] = height;
        matrix_vector_mul(rotation_matrix, cone_co_rot);
        vbo[*offset + 6] = origin_base[0] + cone_co_rot[0];
        vbo[*offset + 7] = origin_base[1] + cone_co_rot[1];
        vbo[*offset + 8] = origin_base[2] + cone_co_rot[2];

        cyllinder_co_rot[0] = radius;
        cyllinder_co_rot[1] = radius;
        cyllinder_co_rot[2] += height;
        matrix_vector_mul(rotation_matrix, cyllinder_co_rot);
        vbo[*offset + 21] = origin_base[0] + cyllinder_co_rot[0];
        vbo[*offset + 22] = origin_base[1] + cyllinder_co_rot[1];
        vbo[*offset + 23] = origin_base[2] + cyllinder_co_rot[2];

        height_operator[0] = 0;
        height_operator[1] = 0;
        height_operator[2] = 1.5 * height;
        matrix_vector_mul(rotation_matrix, height_operator);
        vbo[*offset + 24] = origin_base[0] + height_operator[0];
        vbo[*offset + 25] = origin_base[1] + height_operator[1];
        vbo[*offset + 26] = origin_base[2] + height_operator[2];

        // normals to the cyllinder triangle
        u[0] = vbo[*offset + 3] - vbo[*offset - prev_off + 3];
        u[1] = vbo[*offset + 4] - vbo[*offset - prev_off + 4];
        u[2] = vbo[*offset + 5] - vbo[*offset - prev_off + 5];

        v[0] = vbo[*offset - prev_off + 21] + vbo[*offset - prev_off + 3];
        v[1] = vbo[*offset - prev_off + 22] + vbo[*offset - prev_off + 4];
        v[2] = vbo[*offset - prev_off + 23] + vbo[*offset - prev_off + 5];

        // cross product
        a_cross_b(u, v, n);
        vbo[*normal_offset + 0] = n[0];
        vbo[*normal_offset + 1] = n[1];
        vbo[*normal_offset + 2] = n[2];

        // normals to the cone triangle
        u[0] = vbo[*offset + 6] - vbo[*offset - prev_off + 6];
        u[1] = vbo[*offset + 7] - vbo[*offset - prev_off + 7];
        u[2] = vbo[*offset + 8] - vbo[*offset - prev_off + 8];

        v[0] = vbo[*offset - prev_off + 24] - vbo[*offset - prev_off + 6];
        v[1] = vbo[*offset - prev_off + 25] - vbo[*offset - prev_off + 7];
        v[2] = vbo[*offset - prev_off + 26] - vbo[*offset - prev_off + 8];

        // cross product
        a_cross_b(u, v, n);
        vbo[*normal_offset + 3] = n[0];
        vbo[*normal_offset + 4] = n[1];
        vbo[*normal_offset + 5] = n[2];
        *normal_offset += 18;

        // normals to the cyllinder triangle
        u[0] = vbo[*offset + 3] - vbo[*offset - prev_off + 21];
        u[1] = vbo[*offset + 4] - vbo[*offset - prev_off + 22];
        u[2] = vbo[*offset + 5] - vbo[*offset - prev_off + 23];

        v[0] = vbo[*offset + 21] - vbo[*offset - prev_off + 21];
        v[1] = vbo[*offset + 22] - vbo[*offset - prev_off + 22];
        v[2] = vbo[*offset + 23] - vbo[*offset - prev_off + 23];

        // cross product
        a_cross_b(u, v, n);
        vbo[*normal_offset + 0] = n[0];
        vbo[*normal_offset + 1] = n[1];
        vbo[*normal_offset + 2] = n[2];

        // normals to the cone triangle
        u[0] = vbo[*offset + 6] - vbo[*offset - prev_off + 24];
        u[1] = vbo[*offset + 7] - vbo[*offset - prev_off + 25];
        u[2] = vbo[*offset + 8] - vbo[*offset - prev_off + 26];

        v[0] = vbo[*offset + 24] - vbo[*offset - prev_off + 24];
        v[1] = vbo[*offset + 25] - vbo[*offset - prev_off + 25];
        v[2] = vbo[*offset + 26] - vbo[*offset - prev_off + 26];

        // cross product
        a_cross_b(u, v, n);
        vbo[*normal_offset + 3] = n[0];
        vbo[*normal_offset + 4] = n[1];
        vbo[*normal_offset + 5] = n[2];
        *normal_offset += 18;
        *offset += prev_off;
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
        double mag = sqrt(pow(vector[0], 2) +
                          pow(vector[1], 2) +
                          pow(vector[2], 2));
        double phi = acos(vector[2] / mag);         // z rot
        double theta = atan2(vector[1], vector[0]); // y rot
        double ct = cos(theta);
        double st = sin(theta);
        double cp = cos(phi);
        double sp = sin(phi);
        double rotation_matrix[3][3] = {
            {ct, -st * cp, st * sp},
            {st, cp * ct, -sp * ct},
            {0, sp, cp}};
        double origin_base[3], cpy[3];
        double cyllinder_co_rot[3] = {radius, radius, 0};
        double cone_co_rot[3] = {2 * radius, 2 * radius, 0};
        std::memcpy(origin_base, position, sizeof(double) * 3);
        double n[3], u[3], v[3];
        for (int i = 0; i < (resolution - 1); i++)
        {
            // bottom triangle - cyllinder
            matrix_vector_cpy(rotation_matrix, cyllinder_co_rot, cpy);
            vbo[*offset + 0] = origin_base[0] + cpy[0];
            vbo[*offset + 1] = origin_base[1] + cpy[1];
            vbo[*offset + 2] = origin_base[2] + cpy[2];

            // bottom triangle - cone
            cone_co_rot[2] += height;
            matrix_vector_cpy(rotation_matrix, cone_co_rot, cpy);
            vbo[*offset + 3] = origin_base[0] + cpy[0];
            vbo[*offset + 4] = origin_base[1] + cpy[1];
            vbo[*offset + 5] = origin_base[2] + cpy[2];

            // top triangle - cyllinder
            cyllinder_co_rot[2] += height;
            matrix_vector_cpy(rotation_matrix, cyllinder_co_rot, cpy);
            vbo[*offset + 12] = origin_base[0] + cpy[0];
            vbo[*offset + 13] = origin_base[1] + cpy[1];
            vbo[*offset + 14] = origin_base[2] + cpy[2];

            // top triangle - cone
            matrix_vector_mul(rotation_matrix, height_operator);
            vbo[*offset + 15] = origin_base[0] + height_operator[0];
            vbo[*offset + 16] = origin_base[1] + height_operator[1];
            vbo[*offset + 17] = origin_base[2] + height_operator[2];
            height_operator[0] = 0;
            height_operator[1] = 0;
            height_operator[2] = 1.5 * height;
            cyllinder_co_rot[2] -= height;
            cone_co_rot[2] -= height;

            matrix_vector_mul(t_rotation, cyllinder_co_rot);
            matrix_vector_mul(t_rotation, cone_co_rot);

            if (i > 0)
            {
                // firstly compute the later indices for vertex
                // because we will use them to compute the normals

                // normals to the cyllinder triangle
                u[0] = vbo[*offset + 0] - vbo[*offset - 24 + 12];
                u[1] = vbo[*offset + 1] - vbo[*offset - 24 + 13];
                u[2] = vbo[*offset + 2] - vbo[*offset - 24 + 14];

                v[0] = vbo[*offset + 12] - vbo[*offset - 24 + 12];
                v[1] = vbo[*offset + 13] - vbo[*offset - 24 + 13];
                v[2] = vbo[*offset + 14] - vbo[*offset - 24 + 14];

                // cross product
                a_cross_b(u, v, n);
                vbo[*offset - 24 + 6] = n[0];
                vbo[*offset - 24 + 7] = n[1];
                vbo[*offset - 24 + 8] = n[2];

                // normals to the cone triangle
                u[0] = vbo[*offset + 3] - vbo[*offset - 24 + 15];
                u[1] = vbo[*offset + 4] - vbo[*offset - 24 + 16];
                u[2] = vbo[*offset + 5] - vbo[*offset - 24 + 17];

                v[0] = vbo[*offset + 15] - vbo[*offset - 24 + 15];
                v[1] = vbo[*offset + 16] - vbo[*offset - 24 + 16];
                v[2] = vbo[*offset + 17] - vbo[*offset - 24 + 17];

                // cross product
                a_cross_b(u, v, n);
                vbo[*offset - 24 + 9] = n[0];
                vbo[*offset - 24 + 10] = n[1];
                vbo[*offset - 24 + 11] = n[2];
            }
            *offset += 24;
        }
        // reset rotational vectors to their defaults
        cyllinder_co_rot[0] = radius;
        cyllinder_co_rot[1] = radius;
        cyllinder_co_rot[2] = 0;
        matrix_vector_mul(rotation_matrix, cyllinder_co_rot);
        vbo[*offset + 0] = origin_base[0] + cyllinder_co_rot[0];
        vbo[*offset + 1] = origin_base[1] + cyllinder_co_rot[1];
        vbo[*offset + 2] = origin_base[2] + cyllinder_co_rot[2];

        cone_co_rot[0] = 2 * radius;
        cone_co_rot[1] = 2 * radius;
        cone_co_rot[2] = height;
        matrix_vector_mul(rotation_matrix, cone_co_rot);
        vbo[*offset + 3] = origin_base[0] + cone_co_rot[0];
        vbo[*offset + 4] = origin_base[1] + cone_co_rot[1];
        vbo[*offset + 5] = origin_base[2] + cone_co_rot[2];

        cyllinder_co_rot[0] = radius;
        cyllinder_co_rot[1] = radius;
        cyllinder_co_rot[2] += height;
        matrix_vector_mul(rotation_matrix, cyllinder_co_rot);
        vbo[*offset + 12] = origin_base[0] + cyllinder_co_rot[0];
        vbo[*offset + 13] = origin_base[1] + cyllinder_co_rot[1];
        vbo[*offset + 14] = origin_base[2] + cyllinder_co_rot[2];

        height_operator[0] = 0;
        height_operator[1] = 0;
        height_operator[2] = 1.5 * height;
        matrix_vector_mul(rotation_matrix, height_operator);
        vbo[*offset + 15] = origin_base[0] + height_operator[0];
        vbo[*offset + 16] = origin_base[1] + height_operator[1];
        vbo[*offset + 17] = origin_base[2] + height_operator[2];

        // normals to the cyllinder triangle
        u[0] = vbo[*offset + 0] - vbo[*offset - 24 + 12];
        u[1] = vbo[*offset + 1] - vbo[*offset - 24 + 13];
        u[2] = vbo[*offset + 2] - vbo[*offset - 24 + 14];

        v[0] = vbo[*offset + 12] - vbo[*offset - 24 + 12];
        v[1] = vbo[*offset + 13] - vbo[*offset - 24 + 13];
        v[2] = vbo[*offset + 14] - vbo[*offset - 24 + 14];

        // cross product
        a_cross_b(u, v, n);
        vbo[*offset - 24 + 6] = n[0];
        vbo[*offset - 24 + 7] = n[1];
        vbo[*offset - 24 + 8] = n[2];

        // normals to the cone triangle
        u[0] = vbo[*offset + 3] - vbo[*offset - 24 + 15];
        u[1] = vbo[*offset + 4] - vbo[*offset - 24 + 16];
        u[2] = vbo[*offset + 5] - vbo[*offset - 24 + 17];

        v[0] = vbo[*offset + 15] - vbo[*offset - 24 + 15];
        v[1] = vbo[*offset + 16] - vbo[*offset - 24 + 16];
        v[2] = vbo[*offset + 17] - vbo[*offset - 24 + 17];

        // cross product
        a_cross_b(u, v, n);
        vbo[*offset - 24 + 9] = n[0];
        vbo[*offset - 24 + 10] = n[1];
        vbo[*offset - 24 + 11] = n[2];
        *offset += 24;
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
        int start_index = 0;
        int *indices = (int *)malloc(sizeof(int) * (3 * (index_required - 2) * N));
        for (int n = 0; n < N; n++)
        {
            start_index = n * index_required + 3;
            for (int i = 0; i < (index_required - 2); i++)
            {
                indices[n * (index_required - 2) * 3 + i * 3 + 0] = start_index + i - 3;
                indices[n * (index_required - 2) * 3 + i * 3 + 1] = start_index + i - 2;
                indices[n * (index_required - 2) * 3 + i * 3 + 2] = start_index + i - 1;
            }
        }
        np::dtype dt = np::dtype::get_builtin<int>();
        p::tuple shape = p::make_tuple(3 * (index_required - 2) * N);
        p::tuple stride = p::make_tuple(sizeof(int));
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
        getMifHeader(miffile);
        miffile.close();
    }

    np::ndarray getShapeAsNdarray(double xb, double yb, double zb)
    {
        double *sh = (double *)(malloc(sizeof(double) * xnodes * ynodes * znodes * 3));
        int current_pos = 0;
        for (int z = 0; z < znodes; z++)
        {
            for (int y = 0; y < ynodes; y++)
            {
                for (int x = 0; x < xnodes; x++)
                {
                    sh[current_pos + 0] = xb * (x % xnodes) - xnodes * xb / 2;
                    sh[current_pos + 1] = yb * (y % ynodes) - ynodes * yb / 2;
                    sh[current_pos + 2] = zb * (z % znodes) - znodes * zb / 2;
                    current_pos += 3;
                }
            }
        }
        np::dtype dt = np::dtype::get_builtin<double>();
        p::tuple shape = p::make_tuple(current_pos);
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
                                         p::list negative_color_l,
                                         int sampling)
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
            throw std::invalid_argument("Inflate cannot be 0 or less than 0");
        }

        std::ifstream miffile;
        miffile.open(path, std::ios::out | std::ios_base::binary);
        int buffer_size = getMifHeader(miffile);
        if (buffer_size == 0)
        {
            miffile.close();
            throw std::runtime_error("Invalid mif/ovf file");
        }

        int lines = znodes * xnodes * ynodes;
        char buffer[buffer_size * lines * 3];
        miffile.read(buffer, buffer_size * lines * 3);
        miffile.close();

        double vals[lines * 3];
        if (buffer_size == 4)
        {
            float fvals[lines * 3];
            std::memcpy(fvals, buffer, lines * 3 * sizeof(float));
            for (int i = 0; i < lines * 3; i++)
            {
                vals[i] = fvals[i];
            }
        }
        else if (buffer_size == 8)
        {
            std::memcpy(vals, buffer, lines * 3 * sizeof(double));
        }
        double *fut_ndarray = (double *)(malloc(sizeof(double) * znodes * xnodes * ynodes * 3 * inflate));
        double mag, dot;
        double *array_to_cpy = (double *)(malloc(sizeof(double) * 3));
        int offset = 0;
        int index = 0;

        for (int z = 0; z < znodes; z += 1)
        {
            for (int y = 0; y < ynodes; y += sampling)
            {
                for (int x = 0; x < xnodes; x += sampling)
                {
                    index = 3 * (x + xnodes * y + xnodes * ynodes * z);
                    mag = sqrt(pow(vals[index + 0], 2) +
                               pow(vals[index + 1], 2) +
                               pow(vals[index + 2], 2));
                    if (mag == 0.0)
                        mag = 1.0;
                    dot = (vals[index + 0] / mag) * color_vector[0] +
                          (vals[index + 1] / mag) * color_vector[1] +
                          (vals[index + 2] / mag) * color_vector[2];

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
                    if (array_to_cpy[0] == 0 &&
                        array_to_cpy[1] == 0 &&
                        array_to_cpy[2] == 0)
                    {
                        array_to_cpy[0] = -1;
                        array_to_cpy[1] = -1;
                        array_to_cpy[2] = -1;
                    }
                    for (int inf = 0; inf < inflate; inf++)
                    {
                        std::memcpy(fut_ndarray + offset, array_to_cpy, sizeof(double) * 3);
                        offset += 3;
                    }
                }
            }
        }

        np::dtype dt = np::dtype::get_builtin<double>();
        p::tuple shape = p::make_tuple(offset);
        p::tuple stride = p::make_tuple(sizeof(double));
        return np::from_data(fut_ndarray,
                             dt,
                             shape,
                             stride,
                             p::object());
    }

    np::ndarray getMifVBO(std::string path,
                          int resolution,
                          p::list color_vector_l,
                          p::list positive_color_l,
                          p::list negative_color_l,
                          int sampling,
                          double height,
                          double radius)
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

        std::ifstream miffile;
        miffile.open(path, std::ios::out | std::ios_base::binary);
        int buffer_size = getMifHeader(miffile);
        if (buffer_size == 0)
        {
            miffile.close();
            throw std::runtime_error("Invalid mif/ovf file");
        }

        int lines = znodes * xnodes * ynodes;
        char buffer[buffer_size * lines * 3];
        miffile.read(buffer, buffer_size * lines * 3);
        miffile.close();

        double vals[lines * 3];
        if (buffer_size == 4)
        {
            float fvals[lines * 3];
            std::memcpy(fvals, buffer, lines * 3 * sizeof(float));
            for (int i = 0; i < lines * 3; i++)
            {
                vals[i] = fvals[i];
            }
        }
        else if (buffer_size == 8)
        {
            std::memcpy(vals, buffer, lines * 3 * sizeof(double));
        }
        int size = xnodes * ynodes * znodes * resolution * 10 * 3;
        double *fut_ndarray = (double *)(malloc(sizeof(double) * size));
        double mag, dot;
        double *array_to_cpy = (double *)(malloc(sizeof(double) * 3));

        double pos[3], vec[3], col[3];

        int offset = 0;
        int index = 0;
        int normal_offset = 12;

        double theta = 2 * M_PI / resolution;
        double c = cos(theta);
        double s = sin(theta);
        double t_rotation[3][3] = {
            {c, -s, 0},
            {s, c, 0},
            {0, 0, 1}};
        for (int z = 0; z < znodes; z += 1)
        {
            for (int y = 0; y < ynodes; y += sampling)
            {
                for (int x = 0; x < xnodes; x += sampling)
                {
                    index = 3 * (x + xnodes * y + xnodes * ynodes * z);
                    mag = sqrt(pow(vals[index + 0], 2) +
                               pow(vals[index + 1], 2) +
                               pow(vals[index + 2], 2));
                    if (mag == 0.0)
                        continue;
                    //     mag = 1.0;

                    pos[0] = 1e9 * xbase * (x % xnodes) - xnodes * 1e9 * xbase / 2;
                    pos[1] = 1e9 * ybase * (y % ynodes) - ynodes * 1e9 * ybase / 2;
                    pos[2] = 5e9 * zbase * (z % znodes) - znodes * 5e9 * zbase / 2;
                    vec[0] = vals[index + 0] / mag;
                    vec[1] = vals[index + 1] / mag;
                    vec[2] = vals[index + 2] / mag;
                    dot = vec[0] * color_vector[0] +
                          vec[1] * color_vector[1] +
                          vec[2] * color_vector[2];

                    if (dot > 0)
                    {
                        col[0] = positive_color[0] * dot + (1.0 - dot);
                        col[1] = positive_color[1] * dot + (1.0 - dot);
                        col[2] = positive_color[2] * dot + (1.0 - dot);
                    }
                    else
                    {
                        dot *= -1;
                        col[0] = negative_color[0] * dot + (1.0 - dot);
                        col[1] = negative_color[1] * dot + (1.0 - dot);
                        col[2] = negative_color[2] * dot + (1.0 - dot);
                    }
                    generateVBO(
                        fut_ndarray,
                        &offset,
                        &normal_offset,
                        pos,
                        vec,
                        col,
                        t_rotation,
                        height,
                        radius,
                        resolution);
                }
            }
        }
        printf("OBTAINED SIZE: %d\n", offset);
        np::dtype dt = np::dtype::get_builtin<double>();
        p::tuple shape = p::make_tuple(offset);
        p::tuple stride = p::make_tuple(sizeof(double));
        return np::from_data(fut_ndarray,
                             dt,
                             shape,
                             stride,
                             p::object());
    }

    np::ndarray getArrows(np::ndarray vectors,
                          int resolution,
                          int sampling,
                          double height,
                          double radius)
    {
        int inflate = 6 * resolution;

        double *fut_ndarray = (double *)(malloc(sizeof(double) * znodes * xnodes * ynodes * 3 * inflate));
        double pos[3], vec[3];

        int loc_offset = 0;
        int normal_offset = 6;

        double theta = 2 * M_PI / resolution;
        double c = cos(theta);
        double s = sin(theta);
        double t_rotation[3][3] = {
            {c, -s, 0},
            {s, c, 0},
            {0, 0, 1}};

        int index = 0;
        int final_size = 0;
        for (int z = 0; z < znodes; z += 1)
        {
            for (int y = 0; y < ynodes; y += sampling)
            {
                for (int x = 0; x < xnodes; x += sampling)
                {
                    // index = 3 * (x + xnodes * y + xnodes * ynodes * z);
                    pos[0] = 1e9 * xbase * (x % xnodes) - xnodes * 1e9 * xbase / 2;
                    pos[1] = 1e9 * ybase * (y % ynodes) - ynodes * 1e9 * ybase / 2;
                    pos[2] = 5e9 * zbase * (z % znodes) - znodes * 5e9 * zbase / 2;

                    vec[0] = p ::extract<double>(vectors[index + 0]);
                    vec[1] = p ::extract<double>(vectors[index + 1]);
                    vec[2] = p ::extract<double>(vectors[index + 2]);
                    generateVectors2(fut_ndarray,
                                     &loc_offset,
                                     &normal_offset,
                                     pos,
                                     vec,
                                     t_rotation,
                                     height,
                                     radius,
                                     resolution);
                    index += 3 * 32;
                    final_size += inflate * 3;
                }
            }
        }
        np::dtype dt = np::dtype::get_builtin<double>();
        p::tuple shape = p::make_tuple(final_size);
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
        .def("getMifVBO", &AdvParser::getMifVBO)

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
