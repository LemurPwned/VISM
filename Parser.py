import numpy as np
import pandas as pd

class Parser:
    def __init__():
        self.working_folder = folder

    @staticmethod
    def readFolder(directory):
        pass

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
            print("Wrong file type passed, only .odt")
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
            stages = len(lines) -1
            return df, stages
