import numpy as np
from cython_modules.cython_parse import getLayerOutline
from cython_modules.color_policy import multi_iteration_dot_product
from multiprocessing import Pool
from multiprocessing_parse import asynchronous_pool_order
import scipy.signal
from copy import deepcopy


class ColorPolicy:
    def __init__(self):
        self.averaging_kernel = None
        self.flat_av_kernel = None
        self.mask = None

        self.kernel_size = self.set_kernel_size(3, 2)

    def set_kernel_size(self, kernel_size, dim):
        """
        adjusts the kernel size for a specific array
        This function does not return anything, it sets kernels for
        Color Policy object
        :param kernel_size: is the target kernel size for an array
        """
        self.kernel_size = kernel_size
        if dim == 2:
            self.averaging_kernel = np.ones((self.kernel_size,
                                        self.kernel_size))*(1/(self.kernel_size**2))
        elif dim == 3:
            self.averaging_kernel = np.ones((self.kernel_size, self.kernel_size,
                                        self.kernel_size))*(1/(self.kernel_size**2))
        else:
            raise ValueError("Higher dimensional kernels are not supported")
        self.flat_av_kernel = np.ravel(
                            np.ones((self.kernel_size, 1))*(1/self.kernel_size))


    def linear_convolution(self, matrix):
        """
        performs the linear convlolution on color data given the kernel
        that is defaulted in a Color Policy object upon which the function calls
        :param matrix: matrix to be convoluted
        :return new_color_matrix: returns new color matrix
        """
        pool = Pool()
        multiple_results = [pool.apply_async(self.composite_convolution,
                            (np.array(m), self.averaging_kernel))
                            for m in matrix]
        new_color_matrix = []
        for result in multiple_results:
            convolved_array = result.get(timeout=20)
            new_color_matrix.append(convolved_array)
        return new_color_matrix

    def composite_convolution(self, composite_matrix, kernel):
        """
        performs composite convolution, uses atomic convolutions
        on a composite matrix
        Note that composite matrix is 2D matrix
        :param composite_matrix: matrix to be convoluted
        :param kernel: kernel that is used during convolution
        :return resultant_matrix: returns convolved complex matrix
        """
        resultant_matrix = np.zeros(composite_matrix.shape)
        for i in range(3):
            resultant_matrix[1:-1,1:-1, i] = self.conv2d(composite_matrix[:,:, i],
            kernel)
        return resultant_matrix

    def atomic_convolution(self, vecA, vecB):
        """
        convolves simply two vectors
        :param vecA: vector 1
        :param vecB: vector 2
        :return convolution result
        """
        return np.convolve(vecA, vecB, 'same')

    def conv2d(self, a, f):
        s = f.shape + tuple(np.subtract(a.shape, f.shape) + 1)
        strd = np.lib.stride_tricks.as_strided
        subM = strd(a, shape = s, strides = a.strides * 2)
        return np.einsum('ij,ijkl->kl', f, subM)

    @staticmethod
    def apply_vbo_format(color_array, k=24):
        """
        transforms a given numpy array matrix representing vecotrs in space
        into linear vbo matrix - to fit vertex buffer object
        :param color_array: to be transformed, numpy array
        :param k: indicates how many times should vertex be padded
        """
        pool = Pool()
        output = asynchronous_pool_order(ColorPolicy.color_matrix_flatten, (k, ),
                                            color_array)
        return np.array(output, dtype='float32')

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
    def standard_procedure(outline, color, iterations, averaging, xc, yc, zc,
                            picked_layer='all',
                            vector_set=[[1, 0, 0], [0, 1, 0], [0, 0, 1]],
                            decimate=1,
                            disableDot=True):
        color = np.array(color)
        outline = np.array(outline)
        if type(picked_layer) == int:
            # if single layer is picked modify memory data
            zc = 1
            layer_thickness = xc*yc
            picked_layer = picked_layer*layer_thickness
            color = color[:, picked_layer:picked_layer+layer_thickness, :]
            outline = outline[picked_layer:picked_layer+layer_thickness]

        # input is in form (iterations, zc*yc*xc, 3) and vectors are normalized
        if decimate != 1:
            color = color[:,::decimate,:]
            outline = outline[::decimate, :]
        if averaging != 1:
            averaging_intensity = float(1/averaging)
            # generate mask of shape (zc*yc*xc, 3)
            # take n random numbers (1/averaging)*size
            # step one: generate list of all indices
            mask = np.arange(xc*yc*zc)
            np.random.shuffle(mask)
            mask = mask[:int(len(mask)*averaging_intensity)]
            # now mask is a subset of unqiue, random indices
            for i in range(iterations):
                # zero these random indices for each iteration
                color[i, mask, :] = 0
            # at this point the shape should be conserved (iterations, zc*yc*xc, 3)
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
            assert outline.shape == (zc*yc*xc, 3)
        return dotted_color, outline, decimate
