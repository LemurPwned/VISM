import numpy as np
import math

cimport numpy as np
cimport cython

@cython.boundscheck(False)
@cython.wraparound(False)
def atomic_dot_product(np.ndarray[np.float32_t, ndim=1] color_vector,
                       np.ndarray[np.float32_t, ndim=2] relative_vector_set):
    return [np.dot(color_vector, vector) for vector in relative_vector_set]

@cython.boundscheck(False)
@cython.wraparound(False)
def multi_iteration_dot_product(np.ndarray[np.float32_t, ndim=2] color_iteration,
                                np.ndarray[np.float32_t, ndim=2] vec_set):
    cdef:
        int i
        int ci = color_iteration.shape[0]
    for i in range(0, ci):
        color_iteration[i] = atomic_dot_product(color_iteration[i], vec_set)
    return color_iteration


@cython.boundscheck(False)
@cython.wraparound(False)
def atomic_normalization(np.ndarray[np.float32_t, ndim=2] color_vector):
    return color_vector/np.linalg.norm(color_vector, axis=1, keepdims=True)

@cython.boundscheck(False)
@cython.wraparound(False)
def multi_iteration_normalize(np.ndarray[np.float32_t, ndim=3] color_iterations):
    cdef:
        int i
        int ci = color_iterations.shape[0]
    for i in range(0, ci):
        color_iterations[i] = atomic_normalization(color_iterations[i])
    #np.nan_to_num(color_iterations, copy=False)
    #return color_iterations

@cython.boundscheck(False)
@cython.wraparound(False)
def hyper_contrast_calculation(np.ndarray[np.float32_t, ndim=3] color, xc, yc, zc):
    cdef:
        int i
        int iteration
        int max_it = len(color)
    for iteration in range(0, max_it):
        """
        this is hyper contrast option, enabled via options
        """
        for i in range(0, zc):
            mnR = np.mean(color[iteration, i*xc*yc:(i+1)*xc*yc, 0])
            mnG = np.mean(color[iteration, i*xc*yc:(i+1)*xc*yc, 1])
            mnB = np.mean(color[iteration, i*xc*yc:(i+1)*xc*yc, 2])
            color[iteration, i*xc*yc:(i+1)*xc*yc, 0] -= mnR
            color[iteration, i*xc*yc:(i+1)*xc*yc, 1] -= mnG
            color[iteration, i*xc*yc:(i+1)*xc*yc, 2] -= mnB
            color[iteration, i*xc*yc:(i+1)*xc*yc, 0] *= 10e7
            color[iteration, i*xc*yc:(i+1)*xc*yc, 1] *= 10e7
            color[iteration, i*xc*yc:(i+1)*xc*yc, 2] *= 10e7

def process_vector_to_vbo(iteration,
                          vectors_list,
                          org_cyl_rot,
                          org_cone_rot,
                          t_rotation,
                          height,
                          sides,
                          zero_pad):
    local_vbo = []
    for vector, color in zip(vectors_list, iteration):
        if color.any():
            try:
                cos_x_rot = color[1]
                cos_y_rot = color[0]/math.sqrt(1 - math.pow(color[2],2))
                sin_x_rot = math.sin(math.acos(cos_x_rot))  # radian input
                sin_y_rot = math.sin(math.acos(cos_y_rot))
                rot_matrix = np.array([[cos_y_rot, 0, sin_y_rot],
                                       [sin_y_rot*sin_x_rot, cos_x_rot, -sin_x_rot*cos_y_rot],
                                       [-cos_x_rot*sin_y_rot, sin_x_rot, sin_x_rot*cos_y_rot]])

                vbo = []
                origin_circle = np.array(vector[0:3])
                cylinder_co_rot = org_cyl_rot
                cone_co_rot = org_cone_rot
                # org_cyl_rot = cylinder_co_rot
                # org_cone_rot = cone_co_rot
                for i in range(sides-1):
                    # bottom triangle - cylinder
                    vbo.extend(origin_circle+rot_matrix.dot(cylinder_co_rot))
                    # bottom triangle - cone
                    vbo.extend(origin_circle+rot_matrix.dot(cone_co_rot+height))
                    # top triangle -cylinder
                    vbo.extend(origin_circle+rot_matrix.dot(cylinder_co_rot+height))
                    # top triangle -cone
                    vbo.extend(origin_circle+rot_matrix.dot(height*1.5))
                    cylinder_co_rot = t_rotation.dot(cylinder_co_rot)
                    cone_co_rot = t_rotation.dot(cone_co_rot)

                vbo.extend(origin_circle+rot_matrix.dot(org_cyl_rot))
                vbo.extend(origin_circle+rot_matrix.dot(org_cone_rot+height))
                vbo.extend(origin_circle+rot_matrix.dot(org_cyl_rot+height))
                vbo.extend(origin_circle+rot_matrix.dot(height*1.5))
                local_vbo.extend(vbo)
            except:
                local_vbo.extend(zero_pad)
        else:
            local_vbo.extend(zero_pad)

    return local_vbo

def calculate_layer_colors(x, relative_vector=[0, 1, 0], scale=1):
    dot = np.array([np.inner(i, relative_vector) for i in x])
    angle = np.arccos(dot) ** scale
    angle[np.isnan(angle)] = 0  # get rid of NaN expressions
    return angle
