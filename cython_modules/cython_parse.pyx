import numpy as np
import pandas as pd
import struct
cimport cython


def getFileHeader(filename):
    """
    .omf format reader
    @param filename is a file path
    @return dictionary with headers and their corresponding values
                and number of these headers
    """
    file_header = {}

    with open(filename, 'r') as f:
        g = f.readline()
        while g.startswith('#'):
            g = f.readline()
            if ':' in g:
                x = g.index(':')
                if g[2:x] in file_header:
                    file_header[g[2:x]] += g[x + 1:-1]
                else:
                    file_header[g[2:x]] = g[x + 1:-1]
                try:
                    file_header[g[2:x]] = float(file_header[g[2:x]])
                except:
                    pass
    return file_header


@cython.boundscheck(False)
@cython.wraparound(False)
def normalized(array, axis=-1, order=2):
    l2 = np.atleast_1d(np.linalg.norm(array, order, axis))
    l2[l2==0] = 1
    return array / np.expand_dims(l2, axis)

def parseODTColumn(line):
    """
    This extracts a single column from a odt file
    OOMMF formatting support
    """
    cols = []
    line = line.replace('# Columns: ', '')
    while line != '':
        if line[0] == '{':
            patch = line[1:line.index('}')]
            if patch != '':
                cols.append(patch)
            line = line[line.index('}')+1:]
        else:
            try:
                patch = line[:line.index(' ')]
                if patch != '':
                    cols.append(patch)
                line = line[line.index(' ')+1:]
            except ValueError:
                if line != "" and line != '\n':
                    # last trailing line
                    cols.append(patch)
                line = ""
                break
    return cols

def getPlotData(filename):
    """
    Reads .odt of .txt file
    @param: filename is .odt file path
    @return: dataFrame and stages number
    """
    if filename.endswith('.txt'):
        df = pd.read_table(filename)
        return df, len(df)
    elif filename.endswith('.odt'):
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
        cols = parseODTColumn(cols)
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
    else:
        raise ValueError("Unsupported extension {}".format(filename))


@cython.boundscheck(False)
@cython.wraparound(False)
def getRawVectors(filename):
    """
    processes a .omf filename into a numpy array of vectors
    @param: .omf text file
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
def getLayerOutline(file_header, unit_scaler=1e9):
    """
    constructs the vector outline of each layer, this is a shell that
    colors function operate on (masking)
    @param: file_header is a dictionary form .omf file
    @param: unit_scaler is a unit scaler of dictionary, it indicates
            how much a value stored in a dictionary should be
            multiplied to get a proper unit scale
    @return returns a proper list of vectors creating layer outlines
    """
    xc = int(file_header['xnodes'])
    yc = int(file_header['ynodes'])
    zc = int(file_header['znodes'])
    xb = float(file_header['xbase']) * unit_scaler
    yb = float(file_header['ybase']) * unit_scaler
    zb = float(file_header['zbase']) * unit_scaler
    layers_outline = [[xb * (x%xc), yb * (y%yc), zb * (z%zc)]
            for z in range(zc) for y in range(yc) for x in range(xc)]
    return layers_outline


def process_header(headers):
  """
  processes the header of each .omf file and return base_data dict
  @param: headers specifies header from .omf file
  """
  final_header = {}
  headers = headers.replace(' ', "")
  headers = headers.replace('\\n', "")
  headers = headers.replace('\'b\'', "")
  headers = headers.split('#')
  for header_ in headers:
      if ':' in header_:
          components = header_.split(':')
          if components[1].endswith('b'):
              comp = components[1][:-1]
          else:
              comp = components[1]
          try:
              final_header[components[0]] = float(comp)
          except:
              final_header[components[0]] = components[1]
  return final_header


@cython.boundscheck(False)
@cython.wraparound(False)
def binary_format_reader(filename):
  """
  Reads binary formatted .omf or .ovf files
  """
  header_part = ""
  rawVectorData = None
  header = None
  with open(filename, 'rb') as f:
      x = f.readline()
      while x != b'# End: Header\n':
          header_part += str(x)
          x = f.readline()

      header = process_header(header_part)

      byte_type = f.readline()
      while byte_type == b'#\n':
          byte_type = f.readline()
      # compile struct byte type
      fmt, buff_size, val = decode_byte_size(byte_type)
      struct_object = struct.Struct(fmt)
      test_val = struct_object.unpack(f.read(buff_size))[0]
      if  test_val != val:
          raise ValueError("Invalid file format with validation {} value, \
                              should be {}".format(test_val, val))

      k = int(header['xnodes']*header['ynodes']*header['znodes'])
      rawVectorData = standard_vertex_mode(f, k, struct_object, buff_size)
      f.close()
  assert rawVectorData is not None
  assert header is not None
  return header, rawVectorData


def standard_vertex_mode(f, k, struct_object, buff):
    return np.array([(struct_object.unpack(f.read(buff))[0],
            struct_object.unpack(f.read(buff))[0],
            struct_object.unpack(f.read(buff))[0]) for i in range(int(k))])


def decode_byte_size(byte_format_specification):
    """
    infers byte format based on IEEE header format specification 
    """
    if byte_format_specification == b'# Begin: Data Binary 4\n':
        # float precision - 4 bytes
        fmt = 'f'
        buffer_size = struct.calcsize(fmt)
        four_byte_validation =  1234567.0
        return fmt, buffer_size, four_byte_validation
    elif byte_format_specification == b'# Begin: Data Binary 8\n':
        # double precision - 8 bytes
        fmt = 'd'
        buffer_size = struct.calcsize(fmt)
        eight_byte_validation = 123456789012345.0
        return fmt, buffer_size, eight_byte_validation
    else:
        raise TypeError("Unknown byte specification {}".format(
                                            str(byte_format_specification)))

def genCubes(layer_outline, dims):
    layer_cubed = np.array([cube2(x, dims)
                                    for x in layer_outline]).flatten()
    return layer_cubed, len(layer_cubed)/3

@cython.boundscheck(False)
@cython.wraparound(False)
def subsample(xc, yc, zc, subsample=2):
    """
    creates subsampling index list given number of 
    nodes in each direction and with subsampling given with subsample
    Algorithms subsamples a Fortran-ordered list (row major order)
    @param xc: nodes (cells) in x direction
    @param yc: nodes (cells) in y direction
    @param zc: nodes (cells) in z direction
    @param subsample: nth cell is taken in a given direction if n = subsampling
    """
    xskip = 0
    yskip = 0
    zskip = 0
    index_mask = []
    list_length = xc*yc*zc
    for i in range(list_length):
        if (not xskip%subsample) and (not yskip%subsample) and (not zskip%subsample):
            index_mask.append(i)
        xskip+=1
        if xskip%xc == 0:
            yskip+=1
            xskip = 0
            if yskip%yc == 0:           
                zskip+=1
                yskip = 0
    return np.array(index_mask, dtype=np.int)


def cube(vec, dims=(0.1, 0.1, 0.1)):
    """
    Generates a cuboid with a dimensions specified 
    with front face bottom left corner at vec position
    @param vec: coordinates of face bottom left vertex
    @param dims: dimensions of cuboid (x, y, z)
    """
    vertex_list =[
        # TOP FACE
        vec[0]+dims[0], vec[1], vec[2]+dims[2],
        vec[0], vec[1], vec[2]+dims[2],
        vec[0], vec[1]+dims[1], vec[2]+dims[2],
        vec[0]+dims[0], vec[1]+dims[1], vec[2]+dims[2],
        #BOTTOM FACE
        vec[0]+dims[0], vec[1], vec[2],
        vec[0], vec[1], vec[2],
        vec[0], vec[1]+dims[1], vec[2],
        vec[0]+dims[0], vec[1]+dims[1], vec[2],
        #FRONT FACE
        vec[0]+dims[0], vec[1]+dims[1], vec[2]+dims[2],
        vec[0], vec[1]+dims[1], vec[2]+dims[2],
        vec[0], vec[1]+dims[1], vec[2],
        vec[0]+dims[0], vec[1]+dims[1], vec[2],
        #BACK FACE
        vec[0]+dims[0], vec[1], vec[2]+dims[2],
        vec[0], vec[1], vec[2]+dims[2],
        vec[0], vec[1], vec[2],
        vec[0]+dims[0], vec[1], vec[2],
        #RIGHT FACE
        vec[0]+dims[0], vec[1], vec[2]+dims[2],
        vec[0]+dims[0], vec[1]+dims[1], vec[2]+dims[2],
        vec[0]+dims[0], vec[1]+dims[1], vec[2],
        vec[0]+dims[0], vec[1], vec[2],
        #LEFT FACE
        vec[0], vec[1]+dims[1], vec[2]+dims[2],
        vec[0], vec[1], vec[2]+dims[2],
        vec[0], vec[1], vec[2],
        vec[0], vec[1]+dims[1], vec[2]]
    return vertex_list


def cube2(vec, dims=(0.1, 0.1, 0.1)):
    """
    Generates cube. In opposition to cube function, this 
    can generate cubes of any opacity
    """
    if vec.any():
        vertex_list =[
            # TOP FACE
            vec[0]+dims[0], vec[1], vec[2]+dims[2], vec[3],
            vec[0], vec[1], vec[2]+dims[2], vec[3],
            vec[0], vec[1]+dims[1], vec[2]+dims[2], vec[3],
            vec[0]+dims[0], vec[1]+dims[1], vec[2]+dims[2], vec[3],
            #BOTTOM FACE
            vec[0]+dims[0], vec[1], vec[2], vec[3],
            vec[0], vec[1], vec[2], vec[3],
            vec[0], vec[1]+dims[1], vec[2], vec[3],
            vec[0]+dims[0], vec[1]+dims[1], vec[2], vec[3],
            #FRONT FACE
            vec[0]+dims[0], vec[1]+dims[1], vec[2]+dims[2], vec[3],
            vec[0], vec[1]+dims[1], vec[2]+dims[2], vec[3],
            vec[0], vec[1]+dims[1], vec[2], vec[3],
            vec[0]+dims[0], vec[1]+dims[1], vec[2], vec[3],
            #BACK FACE
            vec[0]+dims[0], vec[1], vec[2]+dims[2], vec[3],
            vec[0], vec[1], vec[2]+dims[2], vec[3],
            vec[0], vec[1], vec[2], vec[3],
            vec[0]+dims[0], vec[1], vec[2], vec[3],
            #RIGHT FACE
            vec[0]+dims[0], vec[1], vec[2]+dims[2], vec[3],
            vec[0]+dims[0], vec[1]+dims[1], vec[2]+dims[2], vec[3],
            vec[0]+dims[0], vec[1]+dims[1], vec[2], vec[3],
            vec[0]+dims[0], vec[1], vec[2], vec[3],
            #LEFT FACE
            vec[0], vec[1]+dims[1], vec[2]+dims[2], vec[3],
            vec[0], vec[1], vec[2]+dims[2], vec[3],
            vec[0], vec[1], vec[2], vec[3],
            vec[0], vec[1]+dims[1], vec[2], vec[3]]
        return vertex_list
    else:
        return np.zeros(96)
