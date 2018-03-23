import numpy as np
from cython_modules.cython_parse import getLayerOutline
from cython_modules.color_policy import multi_iteration_dot_product
from multiprocessing import Pool
import scipy.signal
from copy import deepcopy


def asynchronous_pool_order(func, args, object_list):
    pool = Pool()
    output_list = []
    multiple_results = [pool.apply_async(func, (object_list[i], *args))
                        for i in range(len(object_list))]
    for result in multiple_results:
        value = result.get()
        output_list.append(value)
    return output_list

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
        print("CONVOLUTION SHAPE {}".format(matrix.shape))
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
            resultant_matrix[1:-1,1:-1, i] = self.conv2d(composite_matrix[:,:, i], kernel)
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

    def apply_normalization(self, color_array, xc, yc, zc):
        """
        normalizes a large input color_array to unit vectors
        :param color_array: to be normalized, numpy array
        :param xc: nodes in x direction
        :param yc: nodes in y direction
        :parac zc: nodes in z direction
        """
        pool = Pool()
        if zc > 1:
            multiple_results = [pool.apply_async(
                                self.multilayer_normalization,
                                (color_array[i], xc, yc, zc))
                                for i in range(len(color_array))]
        else:
            multiple_results = [pool.apply_async(
                                self.atomic_normalization,
                                (color_array[i], xc, yc, zc))
                                for i in range(len(color_array))]
        color_array = [result.get(timeout=12) for result
                            in multiple_results]
        return np.array(color_array)

    def multilayer_normalization(self, multilayer_matrix, xc, yc, zc):
        layer_array = []
        for layer in multilayer_matrix:
            layer_array.append(self.atomic_normalization(layer, xc, yc, 1))
        return np.array(layer_array)

    def atomic_normalization(self, color_array, xc, yc, zc):
        """
        performs unit normalization on tiny arrays
        :param xc: nodes in x direction
        :param yc: nodes in y direction
        :parac zc: nodes in z direction
        """
        normalized_color_array = np.array([x/np.linalg.norm(x)
                        if x.any() else [0.0,0.0,0.0] for x in color_array])\
                            .reshape(xc*yc*zc, 3)
        return normalized_color_array

    def apply_vbo_format(self, color_array, k=24):
        """
        transforms a given numpy array matrix representing vecotrs in space
        into linear vbo matrix - to fit vertex buffer object
        :param color_array: to be transformed, numpy array
        :param k: indicates how many times should vertex be padded
        """
        pool = Pool()
        multiple_results = [pool.apply_async(self.color_matrix_flatten,
                                                (p, k)) for p in color_array]
        new_color_matrix = []
        for result in multiple_results:
            repeated_array = result.get(timeout=20)
            new_color_matrix.append(repeated_array)
        return new_color_matrix

    def color_matrix_flatten(self, vector, times):
        return np.repeat(vector, times, axis=0).flatten()

    def apply_dot_product(self, color_array, mode='single'):
        pool = Pool()
        vector_set = [[1, 1, 0], [-1, 0, 1], [0, 1, 0]]
        print("LAYERS? SHAPE CHECK {}".format(color_array.shape))
        if mode == 'multi':
            # if there are mutlilayers
            color_results = [pool.apply_async(self.multilayer_dot_product,
                                              (color_iteration, vector_set))
                             for color_iteration in color_array]
        else:
            color_results = [pool.apply_async(self.unit_matrix_dot_product,
                                              (color_iteration, vector_set))
                             for color_iteration in color_array]
        new_color_matrix = []
        for result in color_results:
            interleaved = result.get(timeout=20)
            new_color_matrix.append(interleaved)
        return np.array(new_color_matrix)

    def multilayer_dot_product(self, multilayer_matrix, vector_set):
        new_ms = []
        for layer in multilayer_matrix:
            new_ms.append(self.unit_matrix_dot_product(layer, vector_set))
        return np.array(new_ms)

    def unit_matrix_dot_product(self, matrix, vector_set):
        """
        takes single iteration matrix and does dot product
        """
        final_matrix = []
        for color in matrix:
            if color.any():
                final_matrix.append(ColorPolicy.atomic_dot_product(color,
                                                                    vector_set))
            else:
                final_matrix.append([0,0,0])
        return np.array(final_matrix)

    # @staticmethod
    # def atomic_dot_product(color_vector, relative_vector_set):
    #     return [np.dot(color_vector, vector) for vector in relative_vector_set]


    def convolutional_averaging(self, matrix, kernel_size, dim=2):
        """
        averages using convolution
        """
        self.kernel_size = self.set_kernel_size(kernel_size, dim)
        # firstly average the color matrix with kernel
        matrix = self.linear_convolution(matrix)
        return np.array(matrix)

    # @staticmethod
    # def multi_iteration_dot_product(color_iteration, vec_set):
    #     for i in range(color_iteration.shape[0]):
    #         color_iteration[i] = ColorPolicy.atomic_dot_product(color_iteration[i],
    #                                                             vec_set)
    #     return color_iteration

    def standard_procedure(self, outline, color, iterations, averaging, xc, yc, zc,
                        picked_layer='all'):
        if type(picked_layer) == int:
            # if single layer is picked modify memory data
            zc = 1
            print("XC {}, YC {}, ZC {}, MUL {}".format(xc, yc, zc, xc*yc*zc))
            layer_thickness = xc*yc
            picked_layer = picked_layer*layer_thickness
            color = color[:, picked_layer:picked_layer+layer_thickness, :]
            outline = outline[picked_layer:picked_layer+layer_thickness]
            print(color.shape)
        # input is in form (iterations, zc*yc*xc, 3) and vectors are normalized
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
        assert color.shape == (iterations, zc*yc*xc, 3)
        vector_set = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]).astype(np.float32)
        dotted_color = asynchronous_pool_order(multi_iteration_dot_product,
                                                (vector_set,), color)
        dotted_color = np.array(dotted_color)
        outline = np.array(outline)
        # this should have shape (iterations, zc*yc*xc, 3)
        assert dotted_color.shape == (iterations, zc*yc*xc, 3)
        assert outline.shape == (zc*yc*xc, 3)
        return dotted_color, outline, mask
