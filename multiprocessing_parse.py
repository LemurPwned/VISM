import numpy as np
import os
import glob
from multiprocessing import Pool
from cython_modules.cython_parse import *
from binaryornot.check import is_binary

def asynchronous_pool_order(func, args, object_list, timeout=20):
    pool = Pool()
    output_list = []
    multiple_results = [pool.apply_async(func, (object_list[i], *args))
                        for i in range(len(object_list))]
    for result in multiple_results:
        output_list.append(result.get(timeout=timeout))
    return output_list

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
        else:
            omf_headers, rawVectorData = MultiprocessingParse.readBinary(
                                                            files_in_directory)
            omf_header = omf_headers[0]
            if not omf_header:
                raise ValueError("no .omf file has been found")
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

        output = asynchronous_pool_order(getRawVectorsBinary, (),
                                                            files_in_directory)
        output = np.array(output)
        omf_headers = output[:, 0]
        rawVectorData = output[:, 1]
        # test this solution, turn dtype object to float 54
        rawVectorData = np.array([x for x in rawVectorData], dtype=np.float64)

        if rawVectorData is None or omf_headers is None:
            raise TypeError("\nNo vectors created")

        assert rawVectorData.dtype == np.float64

        return omf_headers, rawVectorData

    @staticmethod
    def readText(files_in_directory):
        """
        :param files_in_directory: is a list of text filenames in a directory
        :return numpy array of vectors form .omf files
        """
        # use multiprocessing
        text_pool = Pool()
        rawVectorData = []
        rawVectorData = asynchronous_pool_order(getRawVectors, (),
                                                            files_in_directory,
                                                            timeout=20)
        if not rawVectorData:
            raise TypeError("\nNo vectors created")
        assert rawVectorData.dtype == np.float64

        return np.array(rawVectorData)
