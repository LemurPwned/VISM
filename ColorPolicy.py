import numpy as np
from cython_modules.cython_parse import getLayerOutline

class ColorPolicy:
    def __init__(self):
        self.data_structure = 'flattened_array'
        self._DATA_STRUCTURE_TYPES = ['flattened_array', 'interleaved_array', 'tensor_array']

    def apply_normalization(self, color_array):
        pass

    def apply_dot_product(self, color_array):
        pass

    @staticmethod
    def atomic_dot_product(color_vector, relative_vector_set):
        return [np.dot(color_vector, vector) for vector in relative_vector_set]

    def compose_arrow_interleaved_array(self, raw_vector_data, omf_header):
        """
        this function would create the interleaved array for arrow objects i.e.
        start_vertex, stop_vertex, colorR, colorG, colorB
        :param raw_vector_data: is one iteration, matrix of colors
        :param omf_header: is header from .omf file that allows to create layer outline
        :return: 
        """
        interleaved_array = []
        # get start_vertex array
        layer_outline = getLayerOutline(omf_header=omf_header)
        rel_set = [[1, 1, 0], [-1, 0, 1], [0, 1, 0]]
        for vector_begin, vector_tip in zip(layer_outline, raw_vector_data):
            color_type = ColorPolicy.atomic_dot_product(vector_tip, relative_vector_set=rel_set)
            interleaved_array.extend([*vector_begin, *vector_tip, *color_type])
        return interleaved_array
