import numpy as np
import pandas as pd
import struct
cimport cython

def getOmfHeader(filename):
    """
    .omf format reader
    @param filename is .omf file path
    @return dictionary with headers and their corresponding values
                and number of these headers
    """
    omf_header = {}

    with open(filename, 'r') as f:
        g = f.readline()
        while g.startswith('#'):
            g = f.readline()
            if ':' in g:
                x = g.index(':')
                if g[2:x] in omf_header:
                    omf_header[g[2:x]] += g[x + 1:-1]
                else:
                    omf_header[g[2:x]] = g[x + 1:-1]
                try:
                    omf_header[g[2:x]] = float(omf_header[g[2:x]])
                except:
                    pass
    f.close()
    return omf_header


def getOdtData(filename):
    """
    Reads .odt file
    @param filename is .odt file path
    @return dataFrame and stages number
    """
    if not filename.endswith(".odt"):
        print("\nWrong file type passed, only .odt")
        return
    else:
        header_lines = 4
        header = []
        i = 0
        with open(filename, 'r') as f:
            while i < header_lines:
                lines = f.readline()
                header.append(lines)
                i += 1
            units = f.readline()
            lines = f.readlines()
        f.close()
        cols = header[-1]
        cols = cols.replace("} ", "")
        cols = cols.replace("{", "")
        cols = cols.split("Oxs_")
        del cols[0]
        cols = [x.strip() for x in cols]
        dataset = []
        lines = [x.strip() for x in lines]
        lines = [x.split(' ') for x in lines]
        for line in lines:
            temp_line = []
            for el in line:
                try:
                    new_el = float(el)
                    temp_line.append(new_el)
                except:
                    pass
            dataset.append(temp_line)
        dataset = dataset[:-1]
        df = pd.DataFrame.from_records(dataset, columns=cols)
        stages = len(lines) -1
        return df, stages

@cython.boundscheck(False)
@cython.wraparound(False)
def getRawVectors(filename):
    """
    processes a .omf filename into a numpy array of vectors
    @param .omf text file
    @return returns raw_vectors from fortran lists
    """
    raw_vectors = []
    with open(filename, 'r') as f:
        lines = f.readlines()
    f.close()
    raw_vectors = [g.strip().split(' ') for g in lines if '#' not in g]
    raw_vectors = [[float(row[0]), float(row[1]), float(row[2])]
                        for row in raw_vectors]
    return np.array(raw_vectors)

@cython.boundscheck(False)
@cython.wraparound(False)
def getLayerOutline(omf_header, unit_scaler=1e9,
                        layer_skip=False):
    """
    constructs the vector outline of each layer, this is a shell that
    colors function operate on (masking)
    @param omf_header is a dictionary form .omf file
    @param unit_scaler is a unit scaler of dictionary, it indicates
            how much a value stored in a dictionary should be
            multiplied to get a proper unit scale
    @param averaging determines how many vectors to skip before taking the
            next one. Must be alligned with other averaging parameters in
            functions like getRawVectors
    @param layer_skip determines if just one layer should be plotted
    @return returns a proper list of vectors creating layer outlines
    """
    xc = int(omf_header['xnodes'])
    yc = int(omf_header['ynodes'])
    zc = int(omf_header['znodes'])
    xb = float(omf_header['xbase']) * unit_scaler
    yb = float(omf_header['ybase']) * unit_scaler
    zb = float(omf_header['zbase']) * unit_scaler
    if layer_skip:
        zc = 1 #generate just one layer
    layers_outline = [[xb * (x%xc), yb * (y%yc), zb * (z%zc)]
            for z in range(zc) for y in range(yc) for x in range(xc)]
    return layers_outline

def getRawVectorsBinary(filename, averaging=1):
    """
    @param .omf binary file
    @return returns raw_vectors from fortran lists
    use this as it is the fastest way of reading binary files, however,
    this has little error handling
    """
    vectors = []
    base_data = {}
    validation = 123456789012345.0  # this is IEEE validation value
    guard = 0
    constant = 900
    with open(filename, 'rb') as f:
        last = f.read(constant)
        while last != validation:
            guard += 1
            f.seek(constant+guard)
            last = struct.unpack('d', f.read(8))[0]
            f.seek(0)
            if guard > 250:
                raise struct.error
        headers = str(f.read(constant+guard))
        omf_header = process_header(headers)
        k = int(omf_header['xnodes']*omf_header['ynodes']*omf_header['znodes'])
        f.read(8)
        layer_skip = int(omf_header['xnodes']*omf_header['ynodes'])
        layer_num = 3
        s = layer_num*layer_skip
        rawVectorDatavectors = standard_vertex_mode(f, k)
    f.close()

    return omf_header, rawVectorDatavectors

def process_header(headers):
    """
    processes the header of each .omf file and return base_data dict
    """
    omf_header = {}
    headers = headers.replace('\'', "")
    headers = headers.replace(' ', "")
    headers = headers.replace('\\n', "")
    headers = headers.split('#')
    for header in headers:
        if ':' in header:
            components = header.split(':')
            try:
                omf_header[components[0]] = float(components[1])
            except:
                omf_header[components[0]] = components[1]
    return omf_header


@cython.boundscheck(False)
@cython.wraparound(False)
def vbo_vertex_mode(f, k, a= [1,0,1], b =[-1,-1,0]):
    p = []
    for i in range(k):
      x = [struct.unpack('d', f.read(8))[0],
              struct.unpack('d', f.read(8))[0],
              struct.unpack('d', f.read(8))[0]]
      p.append([np.dot(x, a), np.dot(x, b), 0])
    return np.repeat(p, 24, axis=0).flatten()


def standard_vertex_mode(f, k):
    return np.array([(struct.unpack('d', f.read(8))[0],
            struct.unpack('d', f.read(8))[0],
            struct.unpack('d', f.read(8))[0]) for i in range(int(k))])


def generate_cubes(omf_header, spacer, skip=None, layer=None):
    layer_outline = getLayerOutline(omf_header)
    if layer:
      layer_outline = layer_outline[:int(omf_header['xnodes'])*\
                                    int(omf_header['ynodes'])]
      layer_outline = layer_outline[::skip]

    layer_cubed = np.array([cube(x, spacer)
                                    for x in layer_outline]).flatten()
    return layer_cubed, len(layer_cubed)/3

def genCubes(layer_outline, spacer):
    layer_cubed = np.array([cube(x, spacer)
                                    for x in layer_outline]).flatten()
    return layer_cubed, len(layer_cubed)/3

def cube(vec, spacer=0.1):
    vertex_list =[
        vec[0]+spacer, vec[1], vec[2]+spacer,
        vec[0], vec[1], vec[2]+spacer,
        vec[0], vec[1]+spacer, vec[2]+spacer,
        vec[0]+spacer, vec[1]+spacer, vec[2]+spacer,
        #BOTTOM FACE
        vec[0]+spacer, vec[1], vec[2],
        vec[0], vec[1], vec[2],
        vec[0], vec[1]+spacer, vec[2],
        vec[0]+spacer, vec[1]+spacer, vec[2],
        #FRONT FACE
        vec[0]+spacer, vec[1]+spacer, vec[2]+spacer,
        vec[0], vec[1]+spacer, vec[2]+spacer,
        vec[0], vec[1]+spacer, vec[2],
        vec[0]+spacer, vec[1]+spacer, vec[2],
        #BACK FACE
        vec[0]+spacer, vec[1], vec[2]+spacer,
        vec[0], vec[1], vec[2]+spacer,
        vec[0], vec[1], vec[2],
        vec[0]+spacer, vec[1], vec[2],
        #RIGHT FACE
        vec[0]+spacer, vec[1], vec[2]+spacer,
        vec[0]+spacer, vec[1]+spacer, vec[2]+spacer,
        vec[0]+spacer, vec[1]+spacer, vec[2],
        vec[0]+spacer, vec[1], vec[2],
        #LEFT FACE
        vec[0], vec[1]+spacer, vec[2]+spacer,
        vec[0], vec[1], vec[2]+spacer,
        vec[0], vec[1], vec[2],
        vec[0], vec[1]+spacer, vec[2]]
    return vertex_list
