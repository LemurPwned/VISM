import numpy as np
import pandas as pd
import os
import sys
import time

class Parser:
    def __init__():
        self.working_folder = folder

    @staticmethod
    def update_progress_bar(current_i, max_i):
        k = int(current_i*100/max_i)
        sys.stdout.write('\r')
        sys.stdout.write('[%-100s] %d%%'%('='*(k+2),k+1))
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
        num_files = len(files_in_directory)
        for j, filename in enumerate(files_in_directory):
            current_path = os.path.join(directory, filename)
            Parser.update_progress_bar(j, num_files)
            if (filename.endswith(".omf")):
                if multipleOmfHeaders:
                    omf_headers.append(Parser.getOmfHeader(current_path))
                else:
                    if (j == 0):
                        omf_headers = Parser.getOmfHeader(current_path)
                rawVectorData.append(Parser.getRawVectors(current_path))
            elif (filename.endswith(".odt")):
                odt_data = Parser.getOdtData(current_path)

        #catch errors, replace with custom exceptions
        if not omf_headers:
            print("\nNo .omf files found")
            raise TypeError
        if not odt_data:
            print("\nNo .odt file found")
            raise TypeError
        if not rawVectorData:
            print("\nNo vectors created")
            raise TypeError

        return rawVectorData, omf_headers, odt_data

    @staticmethod
    def getRawVectors(filename):
        '''
        @param .omf text file
        @return returns raw_vectors from fortran lists
        '''
        raw_vectors = []
        with open(filename, 'r') as f:
            lines = f.readlines()
        f.close()
        raw_vectors = [g.strip().split(' ') for g in lines if '#' not in g]
        raw_vectors = [[float(row[0]), float(row[1]), float(row[2])]
                            for row in raw_vectors]
        return np.array(raw_vectors)

    @staticmethod
    def getOmfHeader(filename):
        '''
        .omf format reader
        @param filename is .omf file path
        @return dictionary with headers and their corresponding values
                    and number of these headers
        '''
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
