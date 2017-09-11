from shapes import Shape
import numpy as np

class Cube(Shape):
    def __init__(self, size):
        self.create(size)

    def rotate(self, *angles):
        pass

    def translate(self, vector):
        translation_matrix = np.array([[*vector] for i
                                        in range(len(self.vertices))],
                                        dtype=np.float32)
        self.vertices['position'] = self.vertices['position'] + translation_matrix
        self.vertices['normal'] = self.vertices['normal'] + translation_matrix

    def move(self, *position):
        pass

    def create(self, size):
            # Vertices positions
            vtype = [('position', np.float32, 3),
                 ('texcoord', np.float32, 2),
                 ('normal', np.float32, 3),
                 ('color',    np.float32, 4)]
            itype = np.uint32
            p = np.array([[1, 1, 1], [-1, 1, 1], [-1, -1, 1], [1, -1, 1],
                        [1, -1, -1], [1, 1, -1], [-1, 1, -1], [-1, -1, -1]])*0.5*size

            # Face Normals
            n = np.array([[0, 0, 1], [1, 0, 0], [0, 1, 0],
                          [-1, 0, 1], [0, -1, 0], [0, 0, -1]])
            # Vertice colors
            c = np.array([[1, 1, 1, 1], [0, 1, 1, 1], [0, 0, 1, 1], [1, 0, 1, 1],
                          [1, 0, 0, 1], [1, 1, 0, 1], [0, 1, 0, 1], [0, 0, 0, 1]])
            # Texture coords
            t = np.array([[0, 0], [0, 1], [1, 1], [1, 0]])

            faces_p = [0, 1, 2, 3,
                       0, 3, 4, 5,
                       0, 5, 6, 1,
                       1, 6, 7, 2,
                       7, 4, 3, 2,
                       4, 7, 6, 5]

            faces_c = [0, 1, 2, 3,
                       0, 3, 4, 5,
                       0, 5, 6, 1,
                       1, 6, 7, 2,
                       7, 4, 3, 2,
                       4, 7, 6, 5]

            faces_n = [0, 0, 0, 0,
                       1, 1, 1, 1,
                       2, 2, 2, 2,
                       3, 3, 3, 3,
                       4, 4, 4, 4,
                       5, 5, 5, 5]

            faces_t = [0, 1, 2, 3,
                       0, 1, 2, 3,
                       0, 1, 2, 3,
                       3, 2, 1, 0,
                       0, 1, 2, 3,
                       0, 1, 2, 3]

            self.vertices = np.zeros(24, vtype)
            self.vertices['position'] = p[faces_p]
            self.vertices['normal'] = n[faces_n]
            self.vertices['color'] = c[faces_c]
            self.vertices['texcoord'] = t[faces_t]

            self.filled = np.resize(
                np.array([0, 1, 2, 0, 2, 3], dtype=itype), 6 * (2 * 3))

            self.filled += np.repeat(4 * np.arange(6, dtype=itype), 6)
            self.filled = self.filled.reshape((len(self.filled) // 3, 3))

            self.outline = np.resize(
                np.array([0, 1, 1, 2, 2, 3, 3, 0], dtype=itype), 6 * (2 * 4))

            self.outline += np.repeat(4 * np.arange(6, dtype=itype), 8)

            #return self.vertices, self.filled, self.outline
