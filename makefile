convert:
	pyuic5 -x Windows/UI_files/MainWindow.ui -o Windows/MainWindowTemplate.py
	pyuic5 -x Windows/UI_files/animationSettings.ui -o Windows/animationSettingsTemplate.py
	pyuic5 -x Windows/UI_files/PlotSettings.ui -o Windows/PlotSettingsTemplate.py
	pyuic5 -x Windows/UI_files/PerfOptions.ui -o Windows/PerfOptionsTemplate.py
	pyuic5 -x Windows/UI_files/vectorSettings.ui -o Windows/vectorSettingsTemplate.py
cython:
	python3 cython_modules/ex_setup.py build_ext --build-lib cython_modules/build --inplace
