import time
import struct
import numpy as np
import pandas as pd

def extract_base_data(filename):
    '''
    .omf format reader
    returns dictionary with headers and their corresponding values
    and number of these headers
    '''
    base_data = {}
    count = 0
    with open(filename, 'r') as f:
        g = f.readline()
        while g.startswith('#'):
            count += 1
            g = f.readline()
            if ':' in g:
                x = g.index(':')
                if g[2:x] in base_data:
                    base_data[g[2:x]] += g[x + 1:-1]
                else:
                    base_data[g[2:x]] = g[x + 1:-1]
                try:
                    base_data[g[2:x]] = float(base_data[g[2:x]])
                except:
                    pass
    f.close()
    return base_data, count

def fortran_list(filename):
    '''
    this gathers all the vectors from each .omf file
    '''
    vectors = []
    with open(filename, 'r') as f:
        lines = f.readlines()
    f.close()
    vectors = [g.strip().split(' ') for g in lines if '#' not in g]
    vectors = [[float(row[0]), float(row[1]), float(row[2])] for row in vectors]
    return np.array(vectors)

def construct_layer_outline(base_data):
    '''
    constructs the vector outline of each layer, this is a shell that
    colors function operate on (masking)
    '''
    xc = int(base_data['xnodes'])
    yc = int(base_data['ynodes'])
    zc = int(base_data['znodes'])
    xb = float(base_data['xbase']) * 1e9
    yb = float(base_data['ybase']) * 1e9
    zb = float(base_data['zbase']) * 1e9
    base_vectors = [[xb * (x%xc), yb * (y%yc), zb * (z%zc)]
            for z in range(zc) for y in range(yc) for x in range(xc)]
    return base_vectors

def process_fortran_list(fortran_list, xc, yc, zc):
    fortran_list = np.array([x*len(fortran_list)/np.linalg.norm(x)
        for x in np.nditer(fortran_list, flags=['external_loop'])]).reshape(xc*yc*zc,3)
    return fortran_list

def normalize_fortran_list(fortran_list, xc, yc, zc):
    fortran_list = np.array([x/np.linalg.norm(x)
        if x.any() else [0.0,0.0,0.0] for x in fortran_list])\
        .reshape(xc*yc*zc, 3)
    return fortran_list

def process_header(headers):
    '''
    processes the header of each .omf file and return base_data dict
    '''
    base_data = {}
    headers = headers.replace('\'', "")
    headers = headers.replace(' ', "")
    headers = headers.replace('\\n', "")
    headers = headers.split('#')
    for header in headers:
        if ':' in header:
            components = header.split(':')
            try:
                base_data[components[0]] = float(components[1])
            except:
                base_data[components[0]] = components[1]
    return base_data

def odt_reader(filename):
    '''
    this is an .odt file reader
    '''
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

    units = units.split(" ")
    units = [x.strip() for x in units]

    dataset = []
    lines = [x.strip() for x in lines]
    print("{} lines have been read ".format(len(lines)))
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
    iterations = len(lines) -1
    return df, iterations

def binary_reader_error_handling(filename):
    '''
    binary reader with error handling
    '''
    #TODO: improve the speed of filling arrays
    lists = []
    a_tuple = []
    c = 0
    base_data = {}
    validity = False
    iterator = -10
    validation = 123456789012345.0 #this is IEEE validation value
    with open(filename, 'rb') as f:
        while validity == False and iterator < 50:
            headers = f.read(24*38 + iterator) #idk xD
            #print("Header \n",headers)
            headers = str(headers)
            check_value = struct.unpack('d', f.read(8))[0]
            #print(base_data)
            #print("Check value for 8-binary {}".format(check_value))
            if check_value == validation:
                #print("Proper reading commences ...")
                #print("Detected value for 8-binary {}".format(check_value))
                validity = True
                break
            else:
                #print("Validity check failed")
                #print("Adjusting binary size read")
                f.seek(0)
                iterator += 1
        if iterator > 49  : raise TypeError
        base_data = process_header(headers)
        b = f.read(8)
        k = 3*base_data['xnodes']*base_data['ynodes']*base_data['znodes']
        counter = 0
        while b and counter < k:
            try:
                p = struct.unpack('d', b)[0]
                c += 1
                counter += 1
                if c%3 == 0:
                    a_tuple.append(p)
                    lists.append(tuple(a_tuple))
                    a_tuple = []
                    c = 0
                else:
                    a_tuple.append(p)
            except struct.error:
                print(b)
                pass
            b = f.read(8)
        b = f.read(36 + 8) #pro debug process
        #print("last line {}".format(b))
    f.close()
    return base_data, np.array(lists)

def binary_reader(filename):
    '''
    use this as it is the fastest way of reading binary files, however,
    this has little error handling
    '''
    lists = []
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
        base_data = process_header(headers)
        k = base_data['xnodes']*base_data['ynodes']*base_data['znodes']
        f.read(8)
        lists = np.array([(struct.unpack('d', f.read(8))[0],
                struct.unpack('d', f.read(8))[0],
                struct.unpack('d', f.read(8))[0]) for i in range(int(k))])
    f.close()
    return base_data, lists
