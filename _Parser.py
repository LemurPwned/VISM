from Parser import Parser
import pandas
import numpy

def _getOdtData():
    test_filename = "test_folder/voltage-spin-diode.odt"
    test_odt_data, stages = Parser.getOdtData(test_filename)
    assert isinstance(test_odt_data, pandas.DataFrame)
    assert test_odt_data.shape[0] == stages

def _getOmfHeader():
    test_filename = "test_folder/voltage-spin-diode-Oxs_TimeDriver-Magnetization-00-0000000.omf"
    omf_header = Parser.getOmfHeader(test_filename)
    assert isinstance(omf_header, dict)

def _readFolder():
    test_folder = "data/firstData"
    rawVectorData, omf_header, odtData = Parser.readFolder(test_folder)
    assert isinstance(omf_header, dict)
    assert isinstance(odtData, pandas.DataFrame)
    assert isinstance(rawVectorData, numpy.ndarray)

def _getRawVectors():
    test_filename = "test_folder/voltage-spin-diode-Oxs_TimeDriver-Magnetization-00-0000000.omf"
    raw_vectors = Parser.getRawVectors(test_filename)
    assert isinstance(raw_vectors, numpy.ndarray)
    assert raw_vectors.shape[0] != 0

def test_suite():
    _readFolder()
    #test for odt file
    _getOdtData()
    #test for omf file
    _getOmfHeader()
    #test vectors
    _getRawVectors()

    print("\nTests completed successfully")

if __name__ == "__main__":
    test_suite()
