### USE FEWER SELF.VARIABLE  = xxxx


### Function
1. readFolder(directory, multipleOmfHeaders=False)
  -> if multipleOmfHeaders = False then getOmfHeader is returned only for
    one .omf, else returns for each filename in folder
  -> detects filetype (binary/text)
  -> detects file format (.omf, .odt)
  -> processes dataset
  -> returns omfHeader, odtData (for 2d plots), rawVectorData(from .omf)

2. getOdtData(filename)
   -> returns dataFrame with columns as specified in .odt filename
3. getOmfHeader(filename)
  -> returns .omf header in form of a dictionary

2. drawPlot(odtData, canvas, external_iteration=iterator)
  -> odtData should be a Series of a dataFrame odtData e.g.
      odtData contins colums A, B, C of which we want to plot A & B on one plots
      then
      drawPlot(odtData[['A', 'B']], cavnas=None, external_iteration=None,
      update_function=None)

  ->draws plots dynamically on provided canvas
  -> can have external iterating function
