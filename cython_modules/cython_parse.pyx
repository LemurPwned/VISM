import numpy as np
import pandas as pd
import struct
cimport cython


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


