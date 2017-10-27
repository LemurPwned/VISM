### USE FEWER SELF.VARIABLE  = xxxx


### Function
1. readFolder(directory)
  -> detects filetype (binary/text)
  -> detects file format (.omf, .odt)
  -> processes dataset
  -> returns omfHeader, odtData (for 2d plots), rawVectorData(from .omf)

2. drawPlot(odtData, canvas, external_iteration=iterator)
  ->draws plots dynamically on provided canvas
  -> can have external iterating function
