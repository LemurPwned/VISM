import numpy as np
from cython_modules.cython_parse import getLayerOutline, subsample  
from cython_modules.color_policy import multi_iteration_dot_product, \
                                        hyper_contrast_calculation, \
                                        multi_iteration_cross_color, \
                                        multi_iteration_normalize
from multiprocessing import Pool
from multiprocessing_parse import asynchronous_pool_order
import scipy.signal
from copy import deepcopy


class ColorPolicy:      
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

    @staticmethod
    def pad_4f_vertices(color_iteration, vector_array):
        """
        this padding is used to add opacity for each vector in color matrix
        it is mostly used to hide null/NaN objects
        """
        try:
            assert color_iteration.shape == vector_array.shape
        except AssertionError:
            msg = "Color and vector dimensions must match. Not matching with" + \
                    "color {} and vector {}".format(color_iteration.shape, 
                    vector_array.shape)
            raise ValueError(msg)

        vector_array = vector_array.reshape(color_iteration.shape)
        new_vector_list = np.zeros((vector_array.shape[0], 4))
        for i in range(vector_array.shape[0]):
            if color_iteration[i].any():
                new_vector_list[i]= [*vector_array[i], 1.0]
            else:
                new_vector_list[i] = [0.0, 0.0, 0.0, 0.0]
        return new_vector_list

    @staticmethod
    def standard_procedure(outline, color, iterations, subsampling, xc, yc, zc,
                            picked_layer='all',
                            vector_set=[[1, 0, 0], [0, 1, 0], [0, 0, 1]],
                            color_policy_type='Standard',
                            hyperContrast=False):
        """
        this function should be called whenever one of the following is needed:
        - sampling
        - dot product calculation
        @param: disableDot - if True, dot product is omitted
        @param: vector_set - set of 3 vectors used to calculate R, G, B
                components using dot product (valid if disableDot is False)
        @param: picked_layer - determines which layer or all to calculate
        @return: dotted_color, outline, raw_color - return decimating factor,
                    color after dot product (or not) and layer(s) outline
        """
        color = np.array(color)
        outline = np.array(outline)
        print("SUBSAMPLING: {}".format(subsampling))
        expected_color_shape = (zc*xc*yc, 3) if iterations == 1 else (iterations, zc*xc*yc, 3)
        expected_outline_shape = (zc*xc*yc, 3)

        try:
            assert color.shape == (iterations, zc*yc*xc, 3)
        except AssertionError:
            msg = "invalid shape expected {} was {}".format(expected_color_shape, 
                                                            color.shape)
            raise AssertionError(msg)

        try:
            assert outline.shape == (zc*yc*xc, 3)
        except AssertionError:
            msg = "invalid shape expected {} was {}".format(expected_outline_shape, 
                                                            outline.shape)
            raise AssertionError(msg)

        try:
            assert subsampling >= 1
        except AssertionError:
            msg = "Subsampling must be greater than or equal to one"
            raise AssertionError(subsample)

        if subsampling > 1:
            index_list = subsample(xc, yc, zc, subsample=subsampling)
            if xc > 1: xc = xc//subsampling if xc%subsampling == 0 else xc//subsampling +1
            if yc > 1: yc = yc//subsampling if yc%subsampling == 0 else yc//subsampling +1
            if zc > 1: zc = zc//subsampling if zc%subsampling == 0 else zc//subsampling +1
            color = color[:, index_list, :]
            outline = outline[index_list, :]
            expected_color_shape = (iterations, zc*xc*yc, 3)
            expected_outline_shape = (zc*xc*yc, 3)

        outline = ColorPolicy.pad_4f_vertices(color[0], outline)
        # opacity has been added so change expected shapes
        expected_outline_shape = (zc*xc*yc, 4)
        if type(picked_layer) == int or zc == 1:
            # if single layer is picked modify memory data
            layer_thickness = xc*yc
            if zc != 1:
                zc = 1
                picked_layer = picked_layer*layer_thickness
                color = color[:, picked_layer:picked_layer+layer_thickness, :]
                outline = outline[picked_layer:picked_layer+layer_thickness]
            expected_color_shape = (iterations, zc*xc*yc, 3)
            expected_outline_shape = (zc*xc*yc, 3)
            # input is in form (iterations, zc*yc*xc, 3) and vectors are normalized
        if hyperContrast:
            hyper_contrast_calculation(color, xc, yc, zc)
        try:
            assert color.shape == expected_color_shape
        except AssertionError:
            msg = "invalid shape expected {} was {}".format(expected_color_shape, 
                                                            color.shape)
            raise AssertionError(msg)

        vector_set = np.array(vector_set).astype(np.float32)
        # copy original color for arrows
        original_color = np.copy(color)

        # normalize all vectors
        multi_iteration_normalize(color)
        if color_policy_type == 'Standard':
            for i in range(0, iterations):
                color[i, :, :] = multi_iteration_cross_color(color[i], 
                                                                    vector_set[0],
                                                                    vector_set[1],
                                                                    vector_set[2])
        else:
            for i in range(0, iterations):
                color[i, :, :] = multi_iteration_dot_product(color[i], vector_set)
        color = np.array(color)
        outline = np.array(outline)
        # this should have shape (iterations, zc*yc*xc, 3)
        try:
            assert outline.shape == (zc*yc*xc, 4)
        except AssertionError:
            msg = "invalid shape expected {} was {}".format(expected_outline_shape, 
                                                            outline.shape)
            raise AssertionError(msg)
        try:
            assert original_color.shape == expected_color_shape
        except AssertionError:
            msg = "invalid shape expected {} was {}".format(expected_color_shape, 
                                                            original_color.shape)
            raise AssertionError(msg)
        try:
            assert color.shape == expected_color_shape
        except AssertionError:
            msg = "invalid shape expected {} was {}".format(expected_color_shape, 
                                                            color.shape)
            raise AssertionError(msg)

        return color, outline, original_color
