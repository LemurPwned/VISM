import numpy as np
from cython_modules.cython_parse import getLayerOutline
from multiprocessing import Pool
import scipy.signal

class ColorPolicy:
    def __init__(self):
        self.data_structure = 'flattened_array'
        self._DATA_STRUCTURE_TYPES = ['flattened_array', 'interleaved_array',
                                      'tensor_array']
        self.averaging_kernel = None
        self.flat_av_kernel = None
        self.mask = None

        self.kernel_size = self.set_kernel_size(3)

    def set_kernel_size(self, kernel_size):
        """
        adjusts the kernel size for a specific array
        This function does not return anything, it sets kernels for
        Color Policy object
        :param kernel_size: is the target kernel size for an array
        """
        self.kernel_size = kernel_size
        self.averaging_kernel = np.ones((self.kernel_size,
                                    self.kernel_size))*(1/(self.kernel_size**2))
        self.flat_av_kernel = np.ravel(
                            np.ones((self.kernel_size, 1))*(1/self.kernel_size))

    def averaging_policy(self, color_matrix, vector_matrix=None, av_scale=3):
        """
        this function applies the averaging kernel and then samples
        the matrices to return averaged vector
        if no vector matrix is provided, only color_matrix is transformed as if
        it was a vector_matrix
        :param color_matrix: maps color on vector_matrix should be of size N*(k,m)
        where N is number of iterations and (k,m) is vector matrix size
        :param vector_matrix: has shape (k,m) or linear m = 1
        :param av_scale: specifies how much averaging is done
        :return color_matrix: returns averaged matrix
        :return vector_matrix: if vector matrix is given, its size is adjusted
        and new matrix is returned
        """
        self.kernel_size = self.set_kernel_size(av_scale)
        # firstly average the color matrix with kernel
        color_matrix = self.linear_convolution(color_matrix)
        # now take every nth element from both
        color_matrix = np.array([color[::av_scale] for color in color_matrix])
        if vector_matrix:
            vector_matrix = vector_matrix[::av_scale]
            return color_matrix, vector_matrix
        else:
            return color_matrix

    def sampling_policy(self, x_dim, y_dim, prob_x):
        """
        this function samples the array
        """
        return np.random.choice([True, False], (x_dim, y_dim),
                p=[prob_x, 1-prob_x])

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
            resultant_matrix[:,:, i] = self.conv2d(composite_matrix[:,:, i], kernel)
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
        multiple_results = [pool.apply_async(
                            self.atomic_normalization,
                            (color_array[i], xc, yc, zc))
                            for i in range(len(color_array))]
        color_array = [result.get(timeout=12) for result
                            in multiple_results]
        return np.array(color_array)

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

    def apply_vbo_format(self, color_array):
        """
        transforms a given numpy array matrix representing vecotrs in space
        into linear vbo matrix - to fit vertex buffer object
        :param color_array: to be transformed, numpy array
        """
        pool = Pool()
        multiple_results = [pool.apply_async(self.color_matrix_flatten,
                                                (p, 24)) for p in color_array]
        new_color_matrix = []
        for result in multiple_results:
            repeated_array = result.get(timeout=20)
            new_color_matrix.append(repeated_array)
        return new_color_matrix

    def color_matrix_flatten(self, vector, times):
        return np.repeat(vector, times, axis=0).flatten()

    def normalize_flatten_dot_product(self, vector):
        pass

    def apply_dot_product(self, color_array):
        pool = Pool()
        vector_set = [[1, 1, 0], [-1, 0, 1], [0, 1, 0]]
        color_results = [pool.apply_async(self.unit_matrix_dot_product,
                                          (color_iteration, vector_set))
                         for color_iteration in color_array]
        new_color_matrix = []
        for result in color_results:
            interleaved = result.get(timeout=20)
            new_color_matrix.append(interleaved)
        return new_color_matrix

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

    @staticmethod
    def atomic_dot_product(color_vector, relative_vector_set):
        return [np.dot(color_vector, vector) for vector in relative_vector_set]

    @staticmethod
    def compose_arrow_interleaved_array(raw_vector_data, layer_outline):
        """
        this function would create the interleaved array for arrow objects i.e.
        start_vertex, stop_vertex, colorR, colorG, colorB
        :param raw_vector_data: is one iteration, matrix of colors
        :param layer_outline: is layer outline for color mask
        :return: interleaved array, array with vertices and colors interleaved
        """
        interleaved_array = []
        # get start_vertex array
        rel_set = [[1, 1, 0], [-1, 0, 1], [0, 1, 0]]
        for vector_begin, vector_tip in zip(layer_outline, raw_vector_data):
            if vector_tip.any():
                vector_tip /= np.linalg.norm(vector_tip)
                vector_begin /= np.linalg.norm(vector_begin)
                color_type = ColorPolicy.atomic_dot_product(vector_tip,
                                                relative_vector_set=rel_set)
            else:
                color_type = [0,0,0]
            interleaved_array.extend([*vector_begin, *vector_tip, *color_type])
        return interleaved_array


    def convolutional_averaging(self, matrix, kernel_size):
        self.kernel_size = self.set_kernel_size(kernel_size)
        # firstly average the color matrix with kernel
        matrix = self.linear_convolution(matrix)
        return np.array(matrix)

    def tiny_matrix_selector(self, matrix, averaging=0.5):
        if self.mask is None:
            print(matrix.shape, type(matrix))
            if (type(matrix) == np.ndarray) and (matrix.shape[0] > 1):
                self.compose_mask(matrix.shape, averaging)
                return matrix*self.mask
            else:
                raise ValueError("Invalid matrix")
        else:
            return matrix*self.mask

    @staticmethod
    def atomic_mask(matrix, mask):
        return matrix*mask

    def mask_multilayer_matrix(self, multilayer_matrix, averaging):
        if type(multilayer_matrix) is not np.ndarray:
            raise TypeError("Not a numpy array")
        if self.mask is None:
            self.compose_mask(multilayer_matrix.shape[1:], averaging)
        pool = Pool()
        ps = [pool.apply_async(ColorPolicy.atomic_mask, (iteration, self.mask))
                for iteration in multilayer_matrix]
        res = [x.get(timeout=20) for x in ps]
        return np.array(res)

    def compose_mask(self, matrix_shape, averaging):
        averaging_intesity = float(1/averaging)
        mask = np.random.choice(2, size=matrix_shape, p=[1-averaging_intesity,
                                                         averaging_intesity])
        self.mask = mask

    def standard_procedure(self, outline_array, color_array, iterations,
                                averaging, xc, yc, zc, picked_layer='all'):
        # have these 1d arrays turned into proper layered ones
        print(np.array(outline_array).shape)
        print(np.array(color_array).shape)
        layered_outline = np.array(outline_array).reshape(zc, yc, xc, 3)
        layered_color = np.array(color_array).reshape(iterations,
                                                        zc, yc, xc, 3)

        print(layered_outline.shape)
        print(layered_color.shape)

        if picked_layer == 'all':
            # all layers are used
            pass
        elif type(picked_layer) == int:
            # just one layer is considered
            layered_outline = layered_outline[picked_layer]
            layered_color = layered_color[:, picked_layer, :, :, :]
            zc = 1
            print(layered_outline.shape)
            print(layered_color.shape)
            print("LAYERS SELECTED")
            # perform averaging
            # this does not change shape but averages vectors
            layered_color = self.convolutional_averaging(layered_color, averaging)
            # this does not change shape but zeroes the vectors
            # remember to use the same mask for outline in order to match color
            layered_color = self.mask_multilayer_matrix(layered_color, averaging)
            layered_outline = self.tiny_matrix_selector(layered_outline, averaging)
            print(layered_outline.shape)
            print(layered_color.shape)
            # normalize remaining vectorsq
            layered_color = self.apply_normalization(layered_color, xc, yc, zc)
            # apply dot product
            layered_color = self.apply_dot_product(layered_color)
            # return both
            layered_color = np.array(layered_color).reshape(iterations,
                                                                zc*yc*xc, 3)
            layered_outline = layered_outline.reshape(zc*yc*xc, 3)
            print(layered_color.shape, layered_outline.shape)
            return layered_color, layered_outline
