from input_parser import *
from multiprocessing import Pool

import os
import sys


class Assembly:
    def __init__(self, directory):
        self.directory = directory
        self.extension = '.omf'
        self.header_extension = '.odt'
        self.iterations = None

    def read_simulation_files(self):
        file_list = os.listdir(self.directory)
        omf_files = []
        odt_file = None
        for filename in file_list:
            if filename.endswith(self.extension):
                omf_files.append(os.path.join(self.directory, filename))
            elif filename.endswith(self.header_extension):
                odt_file = os.path.join(self.directory, filename)
        if odt_file is None:
            print("Header not found")
        self.iterations = len(omf_files)
        return omf_files, odt_file

    def process_simulation_files(self, omf_files, filetype='binary'):
        base_data = []
        data = []
        file_pool = Pool()
        progress = 0
        if filetype == 'binary':
            multiple_results = [file_pool.apply_async(binary_reader, \
                                    (filename, )) for filename in omf_files]

            for result in multiple_results:
                self.update_progress_bar(progress)
                progress += 1
                tbd, tdf = result.get(timeout=12)
                data.append(tdf)
                if not base_data:
                    base_data.append(tbd)

        elif filetype == 'text':
            base_data, _ = extract_base_data(omf_files[0])
            multiple_results = [file_pool.apply_async(fortran_list, \
                                (filename,)) for filename in omf_files]
            for result in multiple_results:
                self.update_progress_bar(progress)
                progress += 1
                df = result.get(timeout=12)
                data.append(df)
        return data, base_data

    def update_progress_bar(self, i):
        k = (i*100/self.iterations)
        k = int(k)
        sys.stdout.write('\r')
        sys.stdout.write('[%-100s] %d%%'%('='*(k+2),k+2))
        sys.stdout.flush()
        time.sleep(0.02)
