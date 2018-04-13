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
    def guess_file_type(directory):
        supported_extensions = ['.omf', '.ovf']
        voted_extension = None
        files_in_directory = os.listdir(directory)
        # NOTE: decide what extension is found in directory
        # could be both .omf or .ovf but not mixed
        # omit .odt files if not really specified
        for filename in files_in_directory:
            for file_ext in supported_extensions:
                if filename.endswith(file_ext):
                    voted_extension = file_ext
                    break
            if voted_extension is not None:
                break

        #loop may end and the value may still be None, this means invalid directory
        #tbh I am not sure but it helps fix issue
        if voted_extension is None:
            raise ValueError("Invalid Directory")

        print("SUPPORTED EXTENSION DETECTED {}".format(voted_extension))
        files_in_directory = [os.path.join(directory, filename)
                              for filename in files_in_directory
                              if filename.endswith(voted_extension)]
        files_in_directory = sorted(files_in_directory)
        return files_in_directory, voted_extension

    @staticmethod
    def readFolder(directory, multipleOmfHeaders=False):
        """
        dumps process-ready format from directory
        Returns raw numpy array of vectors, omf_header_files and odt data for
        2d plotting
        :param directory
        :return rawVectorData, omf_headers, getOdtData
        """

        files_in_directory, ext = MultiprocessingParse.guess_file_type(
                                                                    directory)

        odt_file = glob.glob(os.path.join(directory, '*.odt'))
        # look for .odt in current directory
        if len(odt_file) > 1:
            raise ValueError(".odt file extension conflict (too many)")
        elif not odt_file:
            raise ValueError("None .odt")

        # NOTE: this should recognize both .omf and .ovf files
        odt_data, stages = getOdtData(odt_file[0])
        stages = glob.glob(os.path.join(directory, '*' + ext))
        test_file = os.path.join(directory, stages[0])

        stages = len(stages)

        if not is_binary(test_file):
            rawVectorData = MultiprocessingParse.readText(files_in_directory)
            file_for_header = glob.glob(os.path.join(directory, '*' + ext))
            # virtually any will do
            if not file_for_header:
                raise ValueError("no .omf  or .ovf file has been found")
            header = getOmfHeader(file_for_header[0])
        else:
            headers, rawVectorData = MultiprocessingParse.readBinary(
                                                        files_in_directory)
            header = headers[0]
            if not header:
                raise ValueError("no .omf or .ovf file has been found")
        return rawVectorData, header, odt_data, stages

    @staticmethod
    def readBinary(files_in_directory):
        """
        :param files_in_directory: is a list of binary filenames
                                   in a directory
        :return numpy array of vectors form .omf files
        """
        text_pool = Pool()

        output = asynchronous_pool_order(binary_format_reader, (),
                                                        files_in_directory)
        output = np.array(output)
        headers = output[:, 0]
        rawVectorData = output[:, 1]
        # test this solution, turn dtype object to float64
        rawVectorData = np.array([x for x in rawVectorData], dtype=np.float64)

        if rawVectorData is None or headers is None:
            raise TypeError("\nNo vectors created")

        assert rawVectorData.dtype == np.float64
        return headers, rawVectorData

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

        return np.array(rawVectorData)
