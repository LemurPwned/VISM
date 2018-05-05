import numpy as np
import os
import glob
from multiprocessing import Pool
from cython_modules.cython_parse import *
from binaryornot.check import is_binary
import re

def asynchronous_pool_order(func, args, object_list, timeout=20):
    pool = Pool()
    output_list = []
    multiple_results = [pool.apply_async(func, (object_list[i], *args))
                        for i in range(len(object_list))]
    for result in multiple_results:
        try:
            output_list.append(result.get(timeout=timeout))
        except TimeoutError:
            print("Function {}: timeout {}".format(func.__name__,
                                                        timeout))
    return output_list

class MultiprocessingParse:
    @staticmethod
    def compose_trigger_list(files, plot_data):
        """
        """
        if files[0].endswith('.ovf'):
            file_len = len(files)
            return MultiprocessingParse.mumax_trigger_list(file_len, plot_data)
        # TODO: FIND A DRIVER NAMES AND IMPLEMENT THEM IF THERE ARE OTHERS
        driver_class = 'MinDriver'
        match_string = '(^.*)(Oxs_' + driver_class + \
                            '-Magnetization-)([0-9]{2})(-)(.*)(.omf)'
        regex = re.compile(match_string)
        st = []
        # probe file
        filename = files[0]
        column_name = None
        try:
            m = regex.search(os.path.basename(filename))
            if m is None:
                raise AttributeError
            column_name = driver_class +'::Iteration'
        except AttributeError:
            driver_class = 'TimeDriver'
            match_string = '(^.*)(Oxs_' + driver_class + \
                                '-Magnetization-)([0-9]{2})(-)(.*)(.omf)'
            column_name = driver_class +'::Iteration'
            regex = re.compile(match_string)
        for filename in files:
            m = regex.search(os.path.basename(filename))
            if m is not None:
                st.append(int(m.groups()[4]))
            else:
                print(filename)
        trigger_list = plot_data.index[plot_data[column_name].isin(st)]
        try:
            assert len(files) == len(trigger_list)
        except AssertionError:
            # duplicates appeared, take first and drop rest
            unique_stages = plot_data[column_name][~plot_data[column_name]\
                                                    .duplicated(keep='first')]
            trigger_list = unique_stages.index[unique_stages.isin(st)]
        return trigger_list

    @staticmethod
    def mumax_trigger_list(file_len, pl_data):
        print("Warning: Mumax format is not fully supported, see documention" + \
                " on how it is currently handled/implemented")
        time_col = '# t (s)'
        # time interval per .ovf file
        time_interval = np.max(pl_data[time_col])/file_len
        times_list = [time_interval*i for i in range(file_len)]
        trigger_list = []
        for time in times_list:
            # matches closest time
            trigger_list.append(pl_data[time_col]\
                    .index[(pl_data[time_col]-time).abs().argsort()[0]])
        return trigger_list

    @staticmethod
    def guess_file_type(directory):
        supported_extensions = [('.omf', '*.odt'), ('.ovf', 'table.txt')]
        voted_extension = None
        files_in_directory = os.listdir(directory)
        # NOTE: decide what extension is found in directory
        # could be both .omf or .ovf but not mixed
        # omit .odt files if not really specified
        for filename in files_in_directory:
            for file_ext in supported_extensions:
                if filename.endswith(file_ext[0]):
                    voted_extension = file_ext
                    break
            if voted_extension is not None:
                break

        # loop may end and the value may still be None,
        # this means invalid directory
        # tbh I am not sure but it helps fix issue
        if voted_extension is None:
            raise ValueError("Invalid Directory")
        print("SUPPORTED EXTENSION DETECTED {}".format(voted_extension))
        files_in_directory = [os.path.join(directory, filename)
                              for filename in files_in_directory
                              if filename.endswith(voted_extension[0])]
        files_in_directory = sorted(files_in_directory)
        return files_in_directory, voted_extension

    @staticmethod
    def readFile(path):
        """
        Function loads one selected file.
        :param path: path to file which user wants to load (String)
        :return: depends on filetype:
            if .odt - odt_data, stages
            if .omf || .ovf - rawVectorData, header
        """
        if ".odt" in path:
            odt_data, stages = getPlotData(path)
            return odt_data, stages

        elif ".omf" in path or ".ovf" in path:
            rawVectorData = None
            if is_binary(path):
                headers, rawVectorData = MultiprocessingParse.readBinary([path])
                header = headers[0]
            elif not is_binary(path):
                rawVectorData = MultiprocessingParse.readText([path])
                header = getFileHeader(path)
            else:
                raise RuntimeError("multiprocessing_parse.py readFile:" +\
                                                    " Can't detect encoding!")
            return rawVectorData, header
        else:
            raise ValueError("Invalid file! Must have .odt, .omf " + \
                                                        "or .ovf extension!")

    @staticmethod
    def readFolder(directory, multipleFileHeaders=False):
        """
        dumps process-ready format from directory
        Returns raw numpy array of vectors, file_header_files and odt data for
        2d plotting
        :param directory
        :return rawVectorData, file_headers, getPlotData
        """

        files_in_directory, ext = MultiprocessingParse.guess_file_type(
                                                                    directory)
        # ext_files = glob.glob(os.path.join(directory, '*' + ext[0]))
        test_file = os.path.join(directory, files_in_directory[0])

        stages = len(files_in_directory)
        plot_file = glob.glob(os.path.join(directory, ext[1]))
        # look for .odt  or .txt in current directory
        if len(plot_file) > 1:
            raise ValueError("plot file extension conflict (too many)")
            #TODO error window
        elif not plot_file or plot_file is None:
            plot_data = None
            plot_file = None

        # NOTE: this should recognize both .omf and .ovf files
        trigger_list = None
        if plot_file is not None:
            plot_data, stages0 = getPlotData(plot_file[0])
            print(stages0, stages)
            if stages0 != stages:
                if stages0 > stages:
                    trigger_list = MultiprocessingParse.\
                                        compose_trigger_list(files_in_directory,
                                                                    plot_data)
                    stages = len(trigger_list)
                    print("TRIGGER LIST : {}, {}".format(stages,
                                                            len(trigger_list)))
                elif stages0 < stages:
                    raise ValueError("Odt cannot have fewer stages that files")
        else:
            plot_data = None

        if not is_binary(test_file):
            rawVectorData = MultiprocessingParse.readText(files_in_directory)
            file_for_header = glob.glob(os.path.join(directory, '*' + ext[0]))
            # virtually any will do
            if not file_for_header:
                raise ValueError("no .omf  or .ovf file has been found")
            header = getFileHeader(file_for_header[0])
        else:
            headers, rawVectorData = MultiprocessingParse.readBinary(
                                                        files_in_directory)
            header = headers[0]
            if not header:
                raise ValueError("no .omf or .ovf file has been found")
        return rawVectorData, header, plot_data, stages, trigger_list

    @staticmethod
    def readBinary(files_in_directory):
        """
        :param files_in_directory: is a list of binary filenames
                                   in a directory
        :return numpy array of vectors form .omf files
        """
        output = asynchronous_pool_order(binary_format_reader, (),
                                                        files_in_directory,
                                                        timeout=20)
        output = np.array(output)
        headers = output[:, 0]
        rawVectorData = output[:, 1]
        # test this solution, turn dtype object to float64
        rawVectorData = np.array([x for x in rawVectorData], dtype=np.float32)

        if rawVectorData is None or headers is None:
            raise TypeError("\nNo vectors created")

        assert rawVectorData.dtype == np.float32
        return headers, rawVectorData

    @staticmethod
    def readText(files_in_directory):
        """
        :param files_in_directory: is a list of text filenames in a directory
        :return numpy array of vectors form .omf files
        """
        # use multiprocessing
        rawVectorData = []
        rawVectorData = asynchronous_pool_order(getRawVectors, (),
                                                        files_in_directory,
                                                        timeout=20)
        if not rawVectorData:
            raise TypeError("\nNo vectors created")
        rawVectorData = np.array(rawVectorData, dtype=np.float32)
        assert rawVectorData.dtype == np.float32
        return rawVectorData
