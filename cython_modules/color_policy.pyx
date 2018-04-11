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
    for i in range(0, ci):
        color_iteration[i] = atomic_dot_product(color_iteration[i], vec_set)
    return color_iteration


@cython.boundscheck(False)
@cython.wraparound(False)
def atomic_normalization(np.ndarray[np.float64_t, ndim=2] color_vector):
    return color_vector/np.linalg.norm(color_vector, axis=1, keepdims=True)

@cython.boundscheck(False)
@cython.wraparound(False)
def multi_iteration_normalize(np.ndarray[np.float64_t, ndim=3] color_iterations):
    cdef:
        int i
        int ci = color_iterations.shape[0]
    for i in range(0, ci):
        color_iterations[i] = atomic_normalization(color_iterations[i])
    return color_iterations
