import numpy as np
import os
import glob
import re
import pandas as pd

from CParseAdvanced.AdvParser import AdvParser
from multiprocessing import Pool
from binaryornot.check import is_binary


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
        stages = len(lines) - 1
        return df, stages
    else:
        raise ValueError("Unsupported extension {}".format(filename))


def asynchronous_pool_order(func, args, object_list, timeout=20):
    """
    This function parallelizes by multiprocessing a given function.
    It operates by iterating a list - object_list and passes each object
    to a new process of function along with additional args with args
    :param func: function that is to be multiprocessed
    :param args: are the additional parameters to the functions (non-iterative)
    if none pass () - an empty tuple
    :param object_list: is the objects that are iterated
    :param timeout: is the timeout for getting value in multiprocessing
    """
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


def determine_if_plot_triggered(plot_file):

    directory = os.path.dirname(plot_file)

    files_in_directory, ext = guess_file_type(directory)
    test_file = os.path.join(directory, files_in_directory[0])

    stages = len(files_in_directory)

    trigger_list = None
    if plot_file is not None:
        plot_data, stages0 = getPlotData(plot_file)
        if stages0 != stages:
            if stages0 > stages:
                """
                stages0 is number of row entries in plot_file e.g. .odt
                stages is number of vector files e.g. .omf
                So if stages0 > stages that means that plot datapoints
                are more dense than animation. For example, each of the 
                animation frames should get more than one datapoints 
                of the plot: 1 frame has 0-22 plot datapoints, 
                2 frame 23-40 etc. Intervals are not always equal!
                """
                trigger_list = compose_trigger_list(files_in_directory,
                                                    plot_data)
                # that was here before but not always true ?
                # check if that persists
                # stages = len(trigger_list)
            elif stages0 < stages:
                """
                for now we assume that there cannot be more than one 
                video frames per one data plot
                """
                raise ValueError("Odt cannot have fewer stages than files")
    else:
        raise ValueError("Empty plot file or cannot read it!")
    return plot_data, trigger_list


def compose_trigger_list(files, plot_data):
    """
    Creates a trigger list.
    Because the number of entries in plot data file is not always (or rarely)
    equal to number of files, it has to be synchronized somehow.
    Thus, for each file, there are multiple plot datapoints assigned.
    How many and when the change will be activated is dependent on
    the trigger list
    """
    if files[0].endswith('.ovf'):
        file_len = len(files)
        return mumax_trigger_list(file_len, plot_data)
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
        column_name = 'Oxs_' + driver_class + '::Iteration'
    except AttributeError:
        driver_class = 'TimeDriver'
        match_string = '(^.*)(Oxs_' + driver_class + \
            '-Magnetization-)([0-9]{2})(-)(.*)(.omf)'
        column_name = 'Oxs_' + driver_class + '::Iteration'
        regex = re.compile(match_string)
    for filename in files:
        m = regex.search(os.path.basename(filename))
        if m is not None:
            st.append(int(m.groups()[4]))
        else:
            print("Regex trigger list mismatch {}".format(filename))
    trigger_list = plot_data.index[plot_data[column_name].isin(st)]
    try:
        assert len(files) == len(trigger_list)
    except AssertionError:
        # duplicates appeared, take first and drop rest
        unique_stages = plot_data[column_name][~plot_data[column_name]
                                               .duplicated(keep='first')]
        trigger_list = unique_stages.index[unique_stages.isin(st)]
    return trigger_list


def mumax_trigger_list(file_len, pl_data):
    print("Warning: Mumax format is not fully supported, see documention" +
          " on how it is currently handled/implemented")
    time_col = '# t (s)'
    # time interval per .ovf file
    time_interval = np.max(pl_data[time_col])/file_len
    times_list = [time_interval*i for i in range(file_len)]
    trigger_list = []
    for time in times_list:
        # matches closest time
        trigger_list.append(pl_data[time_col]
                            .index[(pl_data[time_col]-time).abs().argsort()[0]])
    return trigger_list


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
    files_in_directory = [os.path.join(directory, filename)
                          for filename in files_in_directory
                          if filename.endswith(voted_extension[0])]
    files_in_directory = sorted(files_in_directory)
    return files_in_directory, voted_extension


def readFile(path):
    """
    Function loads one selected file.
    :param path: path to file which user wants to load (String)
    :return: depends on filetype:
        if .odt - odt_data, stages
        if .omf || .ovf - rawVectorData, header
    """
    if ".odt" in path or ".txt" in path:
        odt_data, stages = getPlotData(path)
        return odt_data, stages

    elif ".omf" in path or ".ovf" in path:
        rawVectorData = None
        if is_binary(path):
            headers, rawVectorData = readBinary([
                path])
            header = headers[0]
        elif not is_binary(path):
            headers, rawVectorData = readText([path])
            header = headers[0]
        else:
            raise RuntimeError("multiprocessing_parse.py readFile:" +
                               " Can't detect encoding!")
        return rawVectorData, header
    else:
        raise ValueError("Invalid file! Must have .odt, .omf " +
                         "or .ovf extension!")


def readFolder(directory, multipleFileHeaders=False):
    """
    dumps process-ready format from directory
    Returns raw numpy array of vectors, file_header_files and odt data for
    2d plotting
    :param directory
    :return rawVectorData, file_headers, getPlotData
    """

    files_in_directory, ext = guess_file_type(
        directory)
    test_file = os.path.join(directory, files_in_directory[0])

    stages = len(files_in_directory)
    plot_file = glob.glob(os.path.join(directory, ext[1]))
    # look for .odt  or .txt in current directory
    if len(plot_file) > 1:
        raise ValueError("plot file extension conflict (too many)")
    elif not plot_file or plot_file is None:
        plot_data = None
        plot_file = None

    # NOTE: this should recognize both .omf and .ovf files
    trigger_list = None
    if plot_file is not None:
        plot_data, stages0 = getPlotData(plot_file[0])
        if stages0 != stages:
            if stages0 > stages:
                """
                stages0 is number of row entries in plot_file e.g. .odt
                stages is number of vector files e.g. .omf
                So if stages0 > stages that means that plot datapoints
                are more dense than animation. For example, each of the 
                animation frames should get more than one datapoints 
                of the plot: 1 frame has 0-22 plot datapoints, 
                2 frame 23-40 etc. Intervals are not always equal!
                """
                trigger_list = \
                    compose_trigger_list(files_in_directory,
                                         plot_data)
                # that was here before but not always true ?
                # check if that persists
                # stages = len(trigger_list)
            elif stages0 < stages:
                """
                for now we assume that there cannot be more than one 
                video frames per one data plot
                """
                raise ValueError("Odt cannot have fewer stages than files")
    else:
        plot_data = None

    if not is_binary(test_file):
        header, rawVectorData = readText(
            files_in_directory)
        if not header:
            raise ValueError("no .omf or .ovf file has been found")
    else:
        header, rawVectorData = readBinary(
            files_in_directory)
        if not header:
            raise ValueError("no .omf or .ovf file has been found")
    return rawVectorData, header, plot_data, stages, trigger_list


def readBinary(files_in_directory):
    """
    :param files_in_directory: is a list of binary filenames
                            in a directory
    :return numpy array of vectors form .omf files
    """
    return readBinaryWithC(files_in_directory)


def readBinaryWithC(files_in_directory):
    """
    :param files_in_directory: is a list of binary filenames
                                in a directory
    :return numpy array of vectors form .omf files
    """
    p = AdvParser()
    rawVectorData = []
    for filename in files_in_directory:
        rawVectorData.append(p.getMifAsNdarray(
            filename).astype(np.float32))

    headers = {'xnodes': p.xnodes, 'ynodes': p.ynodes, 'znodes': p.znodes,
               'xbase': p.xbase, 'ybase': p.ybase, 'zbase': p.zbase}
    return headers, rawVectorData


def readText(files_in_directory):
    """
    :param files_in_directory: is a list of text filenames in a directory
    :return numpy array of vectors form .omf files
    """
    # use multiprocessing
    p = AdvParser()
    rawVectorData = []
    rawVectorData = asynchronous_pool_order(p.getOmfToList, (),
                                            files_in_directory,
                                            timeout=20)
    if not rawVectorData:
        raise TypeError("\nNo vectors created")
    rawVectorData = np.array(rawVectorData, dtype=np.float32)
    assert rawVectorData.dtype == np.float32
    headers = {'xnodes': p.xnodes, 'ynodes': p.ynodes, 'znodes': p.znodes,
               'xbase': p.xbase, 'ybase': p.ybase, 'zbase': p.zbase}
    return headers, rawVectorData
