import os
import glob
from multiprocessing import Pool
from cython_modules.cython_parse import *
from binaryornot.check import is_binary


class MultiprocessingParse:
    @staticmethod
    def readFolder(directory, multipleOmfHeaders=False):
        """
        dumps process-ready format from directory
        Returns raw numpy array of vectors, omf_header_files and odt data for
        2d plotting
        :param directory
        :return rawVectorData, omf_headers, getOdtData
        """
        files_in_directory = os.listdir(directory)
        files_in_directory = [os.path.join(directory, filename)
                              for filename in files_in_directory
                              if filename.endswith('.omf')]

        odt_file = glob.glob(os.path.join(directory, '*.odt'))
        # look for .odt in current directory
        if len(odt_file) > 1:
            raise ValueError(".odt file extension conflict (too many)")
        elif not odt_file:
            raise ValueError("None .odt")
        odt_data, stages = getOdtData(odt_file[0])
        stages = glob.glob(os.path.join(directory, '*.omf'))
        test_file = os.path.join(directory, stages[0])
        stages = len(stages)
        if not is_binary(test_file):
            rawVectorData = MultiprocessingParse.readText(files_in_directory)
            omf_file_for_header = glob.glob(os.path.join(directory, '*.omf'))
            # virtually any will do
            if not omf_file_for_header:
                raise ValueError("no .omf file has been found")
            omf_header = getOmfHeader(omf_file_for_header[0])
            omf_header['binary'] = False
        else:
            print("Detected binary")
            omf_headers, rawVectorData = MultiprocessingParse.readBinary(
                                                            files_in_directory)
            omf_header = omf_headers[0]
            omf_header['binary'] = True
            if not omf_header:
                raise ValueError("no .omf file has been found")
        omf_header['averaging'] = 1
        return rawVectorData, omf_header, odt_data, stages

    @staticmethod
    def readBinary(files_in_directory):
        """
        :param files_in_directory: is a list of binary filenames in a directory
        :return numpy array of vectors form .omf files
        """
        text_pool = Pool()
        rawVectorData = []
        omf_headers = []
        text_file_results = [text_pool.apply_async(getRawVectorsBinary,
                                                   (filename, ))
                             for filename in files_in_directory]
        for i, result in enumerate(text_file_results):
            omf_header_data, vector_data = result.get(timeout=20)
            rawVectorData.append(vector_data)
            omf_headers.append(omf_header_data)
        # catch errors, replace with custom exceptions
        if not rawVectorData:
            raise TypeError("\nNo vectors created")
        if not omf_headers:
            raise TypeError("\nNo vectors created")
        return omf_headers, np.array(rawVectorData)

    @staticmethod
    def readText(files_in_directory):
        """
        :param files_in_directory: is a list of text filenames in a directory
        :return numpy array of vectors form .omf files
        """
        # use multiprocessing
        text_pool = Pool()
        rawVectorData = []
        text_file_results = [text_pool.apply_async(getRawVectors,
                                                   (filename, ))
                             for filename in files_in_directory]
        for i, result in enumerate(text_file_results):
            data = result.get(timeout=20)
            rawVectorData.append(data)
        # catch errors, replace with custom exceptions
        if not rawVectorData:
            raise TypeError("\nNo vectors created")

        return np.array(rawVectorData)
