import numpy as np
cimport numpy as np
cimport cython

@cython.boundscheck(False)
@cython.wraparound(False)
def atomic_dot_product(np.ndarray[np.float64_t, ndim=1] color_vector,
                       np.ndarray[np.float32_t, ndim=2] relative_vector_set):
    return [np.dot(color_vector, vector) for vector in relative_vector_set]

@cython.boundscheck(False)
@cython.wraparound(False)
def multi_iteration_dot_product(np.ndarray[np.float64_t, ndim=2] color_iteration,
                                np.ndarray[np.float32_t, ndim=2] vec_set):
    cdef:
        int i
        int ci = color_iteration.shape[0]
        int sd = color_iteration.shape[1]
    for i in range(0, ci):
        color_iteration[i] = atomic_dot_product(color_iteration[i], vec_set)
    return color_iteration
