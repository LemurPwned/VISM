import numpy as np
import math

cimport numpy as np
cimport cython

@cython.boundscheck(False)
@cython.wraparound(False)
def atomic_dot_product(np.ndarray[np.float32_t, ndim=1] color_vector,
                       np.ndarray[np.float32_t, ndim=2] relative_vector_set):
    """
    dot product to be performed on a slice of an color array and 
    a selected vector set 
    (note this is a time slice not a spatial slice)
    """
    return [np.dot(color_vector, vector) for vector in relative_vector_set]

@cython.boundscheck(False)
@cython.wraparound(False)
def multi_iteration_dot_product(np.ndarray[np.float32_t, ndim=2] color_iteration,
                                np.ndarray[np.float32_t, ndim=2] vec_set):
    """
    dot product to be performed on an array of color matrices and 
    a selected vector set (each vector for each of 3 dimensions)
    """
    cdef:
        int i
        int ci = color_iteration.shape[0]
    for i in range(0, ci):
        color_iteration[i] = atomic_dot_product(color_iteration[i], vec_set)
    return color_iteration

@cython.boundscheck(False)
@cython.wraparound(False)
def atomic_normalization(np.ndarray[np.float32_t, ndim=2] color_vector):
    """
    normalization to be performed on a slice of an color array
    (note this is a time slice not a spatial slice)
    """
    return color_vector/np.linalg.norm(color_vector, axis=1, keepdims=True)

@cython.boundscheck(False)
@cython.wraparound(False)
def multi_iteration_normalize(np.ndarray[np.float32_t, ndim=3] color_iterations):
    """
    normalization to be performed on an array of color matrices
    """
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
    """
    this function increases contrast for a given color array
    using linear contrast increase algorithm
    @param color: normalized color array
    @param xc: number of cells in x direction
    @param yc: number of cells in y direction
    @param zc: number of cells in z direction
    """
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

@cython.boundscheck(False)
@cython.wraparound(False)
def process_vector_to_vbo(iteration,
                          vectors_list,
                          org_cyl_rot,
                          org_cone_rot,
                          t_rotation,
                          height,
                          sides,
                          zero_pad):
    """
    creates the arrows basing for each point in color array
    rotation matrix (arrow rotation) is calculated based on
    the magnetisation vector (its unnormalized form)
    @param iteration: current color matrix - normalized in shape (xc*yc*zc) 
                        where xc, yc, zc are numbers of cells in a given direction
    @param vectors_list: baseline for vector drawing - essentially marks the 
                        position of each arrow
    @param org_cyl_rot: original cyllindrical matrix
    @param org_cone_rot: original cone matrix 
    @param t_rotation: initial rotation
    @param height: height of an arrow
    @param sides: resolution (number of steps around a circle) - the 
                    greater this number, the more smoothed edges a
                    cyllinder will have
    @param zero_pad: array to be put if dot_product or rotation is null matrix
    """
    local_vbo = []
    for vector, color in zip(vectors_list, iteration):
        if color.any():
            try:
                cos_x_rot = color[1]
                cos_y_rot = color[0]/math.sqrt(1 - math.pow(color[2],2))
                # values very close to zero might generate some errors
                # mainly because they exceed acos domain
                try:
                    sin_x_rot = math.sin(math.acos(cos_x_rot))  # radian input
                except ValueError:
                    sin_x_rot = 1
                try:
                    sin_y_rot = math.sin(math.acos(cos_y_rot))
                except ValueError:
                    sin_y_rot = 1
                
                rot_matrix = np.array([[cos_y_rot, 0, sin_y_rot],
                        [sin_y_rot*sin_x_rot, cos_x_rot, -sin_x_rot*cos_y_rot],
                        [-cos_x_rot*sin_y_rot, sin_x_rot, sin_x_rot*cos_y_rot]])
            
                origin_circle = np.array(vector[0:3])
                cylinder_co_rot = org_cyl_rot
                cone_co_rot = org_cone_rot               
                for i in range(sides-1):
                    # bottom triangle - cylinder
                    local_vbo.extend([origin_circle+rot_matrix.dot(cylinder_co_rot),
                    # bottom triangle - cone
                                origin_circle+rot_matrix.dot(cone_co_rot+height),
                    # top triangle -cylinder
                                origin_circle+rot_matrix.dot(cylinder_co_rot+height),
                    # top triangle -cone
                                origin_circle+rot_matrix.dot(height*1.5)])
                    cylinder_co_rot = t_rotation.dot(cylinder_co_rot)
                    cone_co_rot = t_rotation.dot(cone_co_rot)

                local_vbo.extend([origin_circle+rot_matrix.dot(org_cyl_rot),
                            origin_circle+rot_matrix.dot(org_cone_rot+height),
                            origin_circle+rot_matrix.dot(org_cyl_rot+height),
                            origin_circle+rot_matrix.dot(height*1.5)])
                # local_vbo.extend(vbo)
                                
            except KeyError:
                local_vbo.extend(zero_pad)
        else:
            local_vbo.extend(zero_pad)
    return local_vbo

def calculate_layer_colors(x, relative_vector=[0, 1, 0], scale=1):
    """
    used by LayerCanvas to calculate matplotlib heatmap
    Uses dot product on a SINGLE relative vector
    @param x: iterative matrix of colors
    @param relative_vector: vector, for which a dot product is calculated against x elements
    @param scale: can be used to increase sensitivity of small dot products
    """
    dot = np.array([np.inner(i, relative_vector) for i in x])
    angle = np.arccos(dot) ** scale
    angle[np.isnan(angle)] = 0  # get rid of NaN expressions
    return angle
