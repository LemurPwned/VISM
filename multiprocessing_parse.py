import os
import glob
import numpy as np
from multiprocessing import Pool
from Windows.Progress import ProgressBar_Dialog
from PyQt5.QtWidgets import QDialog, QProgressBar, QLabel, QHBoxLayout

from cython_parse import *
from binaryornot.check import is_binary

class MultiprocessingParse():
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
        odt_data, stages = getOdtData(odt_file[0])
        stages = glob.glob(os.path.join(directory, '*.omf'))
        test_file = os.path.join(directory,
                            stages[0])
        stages = len(stages)
        averaging = 1
        if not is_binary(test_file):
            rawVectorData = MultiprocessingParse.readText(files_in_directory, averaging)
            omf_file_for_header = glob.glob(os.path.join(directory, '*.omf'))
            # virtually any will do
            if not omf_file_for_header:
                msg = "no .omf file has been found"
                raise ValueError(msg)
                return
            omf_header = getOmfHeader(omf_file_for_header[0])
            omf_header['binary'] = False
        else:
            print("Detected binary")
            omf_headers, rawVectorData = MultiprocessingParse.readBinary(files_in_directory,
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
        text_file_results = [text_pool.apply_async(getRawVectorsBinary,
                            (filename, averaging))
                            for filename in files_in_directory]
        max_len = len(text_file_results)
        for i, result in enumerate(text_file_results):
            omf_header_data, vector_data = result.get(timeout=20)
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
        text_file_results = [text_pool.apply_async(getRawVectors,
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
