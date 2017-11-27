import numpy as np
import pandas as pd
import os
import sys
import time
import glob
import struct

from binaryornot.check import is_binary
from multiprocessing import Pool

from Windows.Progress import ProgressBar_Dialog
from PyQt5.QtWidgets import QDialog, QProgressBar, QLabel, QHBoxLayout

class Parser():
    def __init__(self):
        super(Parser ,self).__init__()

    @staticmethod
    def update_progress_bar(current_i, max_i):
        """
        updates a progress bar
        @param current_i current level loading cap of whole progress bar
        @param max_i maximum level loading cap of the progress bar
        """
        k = int(current_i*100/max_i)
        sys.stdout.write('\r')
        sys.stdout.write('[%-100s] %d%%'%('='*(k+1),k+1))
        sys.stdout.flush()
        time.sleep(0.02)

    @staticmethod
    def readFolder(directory, multipleOmfHeaders=False):
        """
        dumps process-ready format from directory
        Returns raw numpy array of vectors, omf_header_files and odt data for
        2d plotting

        @param directory
        @return rawVectorData, omf_headers, getOdtData
        """
        omf_headers = []
        rawVectorData = []
        odt_data = None
        files_in_directory = os.listdir(directory)
        files_in_directory = [os.path.join(directory, filename)
                for filename in files_in_directory if filename.endswith('.omf')]

        odt_file = glob.glob(os.path.join(directory, '*.odt'))
        # look for .odt in current directory
        if len(odt_file) > 1:
            msg = ".odt file extension conflict (too many)"
            raise ValueError(msg)
        elif not odt_file:
            msg = "None .odt"
            raise ValueError(msg)
        odt_data, stages = Parser.getOdtData(odt_file[0])
        stages = glob.glob(os.path.join(directory, '*.omf'))
        test_file = os.path.join(directory,
                            stages[0])
        stages = len(stages)
        averaging = 1
        if not is_binary(test_file):
            rawVectorData = Parser.readText(files_in_directory, averaging)
            omf_file_for_header = glob.glob(os.path.join(directory, '*.omf'))
            # virtually any will do
            if not omf_file_for_header:
                msg = "no .omf file has been found"
                raise ValueError(msg)
                return
            omf_header = Parser.getOmfHeader(omf_file_for_header[0])
            omf_header['binary'] = False
        else:
            print("Detected binary")
            omf_headers, rawVectorData = Parser.readBinary(files_in_directory,
                                                        averaging)
            omf_header = omf_headers[0]
            omf_header['binary'] = True
            if not omf_header:
                msg = "no .omf file has been found"
                raise ValueError(msg)
        omf_header['averaging'] = 1
        return rawVectorData, omf_header, odt_data, stages

    @staticmethod
    def readBinary(files_in_directory, averaging):
        """
        @param files_in_directory is a list of binary filenames in a directory
        @return numpy array of vectors form .omf files
        """
        text_pool = Pool()
        rawVectorData = []
        omf_headers = []
        for filename in files_in_directory:
            omf_header_data, vector_data = Parser.getRawVectorsBinary(filename,
                                                                    averaging)
            rawVectorData.append(vector_data)
            omf_headers.append(omf_header_data)
        #catch errors, replace with custom exceptions
        if not rawVectorData:
            print("\nNo vectors created")
            raise TypeError
        if not omf_headers:
            print("\nNo vectors created")
            raise TypeError
        return omf_headers, np.array(rawVectorData)

    @staticmethod
    def readText(files_in_directory, averaging):
        """
        @param files_in_directory is a list of text filenames in a directory
        @return numpy array of vectors form .omf files
        """
        #use multiprocessing
        text_pool = Pool()
        rawVectorData = []
        text_file_results = [text_pool.apply_async(Parser.getRawVectors,
                            (filename, averaging))
                            for filename in files_in_directory]
        max_len = len(text_file_results)
        for i, result in enumerate(text_file_results):
            data = result.get(timeout=20)
            rawVectorData.append(data)
        #catch errors, replace with custom exceptions
        if not rawVectorData:
            print("\nNo vectors created")
            raise TypeError

        return np.array(rawVectorData)

    @staticmethod
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

    @staticmethod
    def getLayerOutlineFromFile(filename, unit_scaler=1e9):
        """
        constructs the vector outline of each layer, this is a shell that
        colors function operate on (masking)
        @param filename (path) of a .omf file
        @return returns a proper list of vectors creating layer outlines
        """
        omf_header = Parser.getOmfHeader(filename)
        xc = int(omf_header['xnodes'])
        yc = int(omf_header['ynodes'])
        zc = int(omf_header['znodes'])
        xb = float(omf_header['xbase']) * unit_scaler
        yb = float(omf_header['ybase']) * unit_scaler
        zb = float(omf_header['zbase']) * unit_scaler
        layers_outline = [[xb * (x%xc), yb * (y%yc), zb * (z%zc)]
                for z in range(zc) for y in range(yc) for x in range(xc)]
        return layers_outline

    @staticmethod
    def getRawVectors(filename, averaging=1, layer_num=3):
        """
        processes a .omf filename into a numpy array of vectors
        @param .omf text file
        @param averaging determines how many vectors to skip before taking the
                next one. Must be alligned with other averaging parameters in
                functions like getRawVectors
        @return returns raw_vectors from fortran lists
        """
        raw_vectors = []
        with open(filename, 'r') as f:
            lines = f.readlines()
        f.close()
        layer_skip = 35*35
        p = layer_num*layer_skip
        raw_vectors = [g.strip().split(' ') for g in lines if '#' not in g]
        raw_vectors = [[float(row[0]), float(row[1]), float(row[2])]
                            for row in raw_vectors[p:p+layer_skip]]
        return np.array(raw_vectors)[0::averaging]

    @staticmethod
    def getRawVectorsVBO(filename):
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
        raw_vectors = [[float(row[0]), float(row[1]), float(row[2])] for
                            i in range(24) for row in raw_vectors]
        return np.array(raw_vectors).flatten()

    @staticmethod
    def getRawVectorsBinary(filename, averaging):
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
            omf_header = Parser.process_header(headers)
            k = omf_header['xnodes']*omf_header['ynodes']*omf_header['znodes']
            f.read(8)
            layer_skip = int(omf_header['xnodes']*omf_header['ynodes'])
            layer_num = 3
            s = layer_num*layer_skip
            rawVectorDatavectors = Parser.vbo_vertex_mode(f, k)
        f.close()
        return omf_header, rawVectorDatavectors

    @staticmethod
    def vbo_vertex_mode(f, k):
        p = np.array([[struct.unpack('d', f.read(8))[0],
                struct.unpack('d', f.read(8))[0],
                struct.unpack('d', f.read(8))[0]] for i in range(int(k))])
        return np.repeat(p, 24, axis=0).flatten()

    @staticmethod
    def standard_vertex_mode(f, k):
        return np.array([(struct.unpack('d', f.read(8))[0],
                struct.unpack('d', f.read(8))[0],
                struct.unpack('d', f.read(8))[0]) for i in range(int(k))])

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def generate_cubes(omf_header, spacer):
        layer_outline = Parser.getLayerOutline(omf_header)
        layer_cubed = np.array([Parser.cube(x, spacer) for x in layer_outline]).flatten()
        return layer_cubed, len(layer_cubed)/3

    @staticmethod
    def cube(vec, spacer=0.1):
        v1 =[
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
        return v1