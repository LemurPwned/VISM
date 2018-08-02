import numpy as np
from cython_modules.cython_parse import getLayerOutline, subsample  
from cython_modules.color_policy import multi_iteration_dot_product, \
                                        hyper_contrast_calculation
from multiprocessing import Pool
from multiprocessing_parse import asynchronous_pool_order
import scipy.signal
from copy import deepcopy


class ColorPolicy:
    def __init__(self):
        self.averaging_kernel = None
        self.flat_av_kernel = None
        self.mask = None
        
    @staticmethod
    def apply_vbo_format(color_array, k=24):
        """
        transforms a given numpy array matrix representing vectors in space
        into linear vbo matrix - to fit vertex buffer object
        :param color_array: to be transformed, numpy array
        :param k: indicates how many times should vertex be padded
        """
        output = asynchronous_pool_order(ColorPolicy.color_matrix_flatten, (k, ),
                                            color_array)
        return np.array(output, dtype='float32')

    @staticmethod
    def apply_vbo_interleave_format(vector_array, color_array):
        output = asynchronous_pool_order(ColorPolicy.interleave,
                                            (vector_array,), color_array)
        return np.array(output, dtype='float32')

    @staticmethod
    def interleave(color_iteration, vector_array):
        """
        uses OpenGl interleaving techniques to construct VBO array
        """
        interleaved = []
        for v, c in zip(vector_array, color_iteration):
            # here add extra one for 4f visibility feature
            if c.any():
                interleaved.extend([*v, v[0]+c[0], v[1]+c[1], v[2]+c[2], 1])
            else:
                interleaved.extend([*v, v[0]+c[0], v[1]+c[1], v[2]+c[2], 0])
        return interleaved

    @staticmethod
    def color_matrix_flatten(vector, times):
        return np.repeat(vector, times, axis=0).flatten()

    def convolutional_averaging(self, matrix, kernel_size, dim=2):
        """
        averages using convolution
        """
        self.kernel_size = self.set_kernel_size(kernel_size, dim)
        # firstly average the color matrix with kernel
        matrix = self.linear_convolution(matrix)
        return np.array(matrix)

    @staticmethod
    def pad_4f_vertices(color_iteration, vector_array):
        """
        this padding is used to add opacity for each vector in color matrix
        it is mostly used to hide null/NaN objects
        """
        assert color_iteration.shape == vector_array.shape
        vector_array = vector_array.reshape(color_iteration.shape)
        new_vector_list = np.zeros((vector_array.shape[0], 4))
        for i in range(vector_array.shape[0]):
            if color_iteration[i].any():
                new_vector_list[i]= [*vector_array[i], 1.0]
            else:
                new_vector_list[i] = [0.0, 0.0, 0.0, 0.0]
        return new_vector_list

    @staticmethod
    def standard_procedure(outline, color, iterations, averaging, xc, yc, zc,
                            picked_layer='all',
                            vector_set=[[1, 0, 0], [0, 1, 0], [0, 0, 1]],
                            decimate=1,
                            disableDot=True,
                            hyperContrast=False):
        """
        this function should be called whenever one of the following is needed:
        - sampling
        - decimation (pseudosampling)
        - dot product calculation
        @param: disableDot - if True, dot product is omitted
        @param: vector_set - set of 3 vectors used to calculate R, G, B
                components using dot product (valid if disableDot is False)
        @param: picked_layer - determines which layer or all to calculate
        @return: dotted_color, outline, decimate - return decimating factor,
                    color after dot product (or not) and layer(s) outline
        """
        subsampling = averaging  # thats a wrapper - refactor later
        color = np.array(color)
        outline = np.array(outline)
        if subsampling > 1:
            index_list = subsample(xc, yc, zc, subsample=subsampling)
            xc = xc//subsampling
            zc = zc//subsampling
            yc = yc//subsampling
            color = color[:, index_list, :]
            outline = outline[index_list, :]
        outline = ColorPolicy.pad_4f_vertices(color[0], outline)

        if type(picked_layer) == int:
            # if single layer is picked modify memory data
            zc = 1
            layer_thickness = xc*yc
            picked_layer = picked_layer*layer_thickness
            color = color[:, picked_layer:picked_layer+layer_thickness, :]
            outline = outline[picked_layer:picked_layer+layer_thickness]
        # input is in form (iterations, zc*yc*xc, 3) and vectors are normalized
        if hyperContrast:
            hyper_contrast_calculation(color, xc, yc, zc)
        if not decimate:
            assert color.shape == (iterations, zc*yc*xc, 3)
        vector_set = np.array(vector_set).astype(np.float32)
        if not disableDot:
            dotted_color = asynchronous_pool_order(multi_iteration_dot_product,
                                                    (vector_set,), color)
        else:
            dotted_color = color
        dotted_color = np.array(dotted_color)
        outline = np.array(outline)
        # this should have shape (iterations, zc*yc*xc, 3)
        if not decimate:
            assert dotted_color.shape == (iterations, zc*yc*xc, 3)
            assert outline.shape == (zc*yc*xc, 4)
        assert dotted_color.shape == (iterations, zc*xc*yc, 3)
        assert color.shape == (iterations, zc*xc*yc, 3)
        return dotted_color, outline, np.array(color)
