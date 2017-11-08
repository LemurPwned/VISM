from Parser import Parser
import pandas
import numpy
import time


def _getOdtData():
    test_filename = "test_folder/voltage-spin-diode.odt"
    test_odt_data, stages = Parser.getOdtData(test_filename)
    assert isinstance(test_odt_data, pandas.DataFrame)
    assert test_odt_data.shape[0] == stages

def _getOmfHeader():
    test_filename = "test_folder/voltage-spin-diode-Oxs_TimeDriver-Magnetization-00-0000000.omf"
    omf_header = Parser.getOmfHeader(test_filename)
    assert isinstance(omf_header, dict)

def _readFolderText():
    print("\nTEXT FILE TEST ...")
    test_folder = "data/firstData"
    start = time.time()
    rawVectorData, omf_header, odtData, stages = Parser.readFolder(test_folder)
    stop = time.time()
    assert isinstance(omf_header, dict)
    assert isinstance(odtData, pandas.DataFrame)
    assert isinstance(rawVectorData, numpy.ndarray)
    print("\nSUCCESS")
    print("TOOK: {} s".format(stop-start))

def _readFolderBinary():
    print("\nBINARY FILE TEST ... ")
    test_folder = "data/0520nm"
    start = time.time()
    rawVectorData, omf_header, odtData, stages = Parser.readFolder(test_folder)
    stop = time.time()
    assert isinstance(stages, int)
    assert isinstance(omf_header, dict)
    assert isinstance(odtData, pandas.DataFrame)
    assert isinstance(rawVectorData, numpy.ndarray)
    print("\nSUCCESS")
    print("TOOK: {} s".format(stop-start))

def _getRawVectors():
    test_filename = "test_folder/voltage-spin-diode-Oxs_TimeDriver-Magnetization-00-0000000.omf"
    raw_vectors = Parser.getRawVectors(test_filename)
    assert isinstance(raw_vectors, numpy.ndarray)
    assert raw_vectors.shape[0] != 0

def test_suite():
    #test for odt file
    _getOdtData()
    #test for omf file
    _getOmfHeader()
    #test vectors
    _getRawVectors()
    #integrate
    _readFolderText()
    _readFolderBinary()

    print("\nTests completed successfully")

if __name__ == "__main__":
    test_suite()
