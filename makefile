convert:
	pyuic5 -x Windows/UI_files/MainWindow.ui -o MainWindowTemplate.py
	pyuic5 -x Windows/UI_files/animationSettings.ui -o animationSettingsTemplate.py
	pyuic5 -x Windows/UI_files/PlotSettings.ui -o PlotSettingsTemplate.py
	pyuic5 -x Windows/UI_files/PerfOptions.ui -o PerfOptionsTemplate.py

cython:
	python3 cython_modules/setup.py build_ext --build-lib cython_modules/build 
