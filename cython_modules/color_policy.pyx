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
        color_iteration[i] = [0.5*(np.dot(color_iteration[i], vector)+1) for vector in vec_set]
    return color_iteration

@cython.boundscheck(False)
@cython.wraparound(False)
def multi_iteration_cross_color(np.ndarray[np.float32_t, ndim=2] color_iteration,
                                np.ndarray[np.float32_t, ndim=1] user_vector,
                                np.ndarray[np.float32_t, ndim=1] negative_color, 
                                np.ndarray[np.float32_t, ndim=1] positive_color):
    """
    s is dot product
    positive color is when s > 0
    negative color is when s < 0
    """
    cdef:
        float s
        int i
        int ci = color_iteration.shape[0]
    white = np.array([1, 1, 1], np.float32)
    for i in range(0, ci):
        s = np.dot(color_iteration[i], user_vector)
        abs_s = np.abs(s)
        if s > 0:
            color_iteration[i] = abs_s*positive_color + (1-abs_s)*white
        else:
            color_iteration[i] = abs_s*negative_color + (1-abs_s)*white
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
        color_iterations[i] = color_iterations[i]/np.linalg.norm(color_iterations[i], 
                                                    axis=1, keepdims=True)
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
            color[iteration, i*xc*yc:(i+1)*xc*yc, 0] *= 10e5
            color[iteration, i*xc*yc:(i+1)*xc*yc, 1] *= 10e5
            color[iteration, i*xc*yc:(i+1)*xc*yc, 2] *= 10e5

@cython.boundscheck(False)
@cython.wraparound(False)
def process_vector_to_vbo(iteration,
                          vectors_list,
                          org_cyl_rot,
                          org_cone_rot,
                          t_rotation,
                          height,
                          sides):
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
    cdef:
        int iteration_len = len(iteration)
        int p = 0
        int j, i
    local_vbo = np.ndarray((iteration_len*sides*4, 3), dtype=np.float32)
    for j in range(0, iteration_len):
        if iteration[j].any():
            mag = math.sqrt(math.pow(iteration[j,0], 2)
                            +math.pow(iteration[j,1], 2)
                            +math.pow(iteration[j,2], 2))
            phi = math.acos(iteration[j, 2]/mag) # z rotation
            theta = math.atan2(iteration[j, 1], iteration[j, 0]) # y rotation

            ct = math.cos(theta)
            st = math.sin(theta)
            cp = math.cos(phi)
            sp = math.sin(phi)
            # perform in the order Z_ROT x X_ROT as firstly we rotate x, then Z
            rot_matrix = np.array([
                [ct, -st*cp, st*sp],
                [st, cp*ct, -sp*ct],
                [0, sp, cp]
            ])
            origin_circle = np.array(vectors_list[j, 0:3])
            cylinder_co_rot = org_cyl_rot
            cone_co_rot = org_cone_rot        
            for _ in range(sides-1):      
                # bottom triangle - cylinder              
                local_vbo[p, :] = origin_circle+rot_matrix.dot(cylinder_co_rot) 
                # bottom triangle - cone
                local_vbo[p+1, :] = origin_circle+rot_matrix.dot(cone_co_rot+height)
                # top triangle - cylinder
                local_vbo[p+2, :] = origin_circle+rot_matrix.dot(cylinder_co_rot+height)
                # top triangle - cone  (cone tip)
                local_vbo[p+3, :] = origin_circle+rot_matrix.dot(height*1.5) 
                p+=4 
                cylinder_co_rot = t_rotation.dot(cylinder_co_rot)
                cone_co_rot = t_rotation.dot(cone_co_rot)
            # last ones are to cover the circle (end up in the starting point)
            # this is required by the way graphics card wants to join the points
            local_vbo[p, :] = origin_circle+rot_matrix.dot(org_cyl_rot) 
            local_vbo[p+1, :] = origin_circle+rot_matrix.dot(org_cone_rot+height)
            local_vbo[p+2, :] = origin_circle+rot_matrix.dot(org_cyl_rot+height) 
            local_vbo[p+3, :] = origin_circle+rot_matrix.dot(height*1.5)  
            p+=4     
    return local_vbo

def compute_normals_cubes(vertex_values, cube_number):  
    """
    each cube has 8 faces. there is cube_number*8 faces in total
    each face is composed of 4 vertices
    """
    cdef:
        float normal_value = 0.0
        int max_range = len(vertex_values)/3
        int vertices_per_face = 4 # cubes have 6 faces, each face - 4 vertices,
    normals_vbo = np.ndarray((max_range, 3), dtype='float32')
    for i in range(0, max_range):
        normal_value += np.cross(vertex_values[i+1] - vertex_values[i],
                                 vertex_values[i+2] - vertex_values[i])
        if i%vertices_per_face == 0 and i > 0:
            normals_vbo[i] = normal_value
            normal_value = 0
    return normals_vbo

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
