convert:
	pyuic5 -x ../Windows/UI_files/MainWindow.ui -o ../Windows/Templates/MainWindowTemplate.py
	pyuic5 -x ../Windows/UI_files/animationSettings.ui -o ../Windows/Templates/animationSettingsTemplate.py
	pyuic5 -x ../Windows/UI_files/PlotSettings.ui -o ../Windows/Templates/PlotSettingsTemplate.py
	pyuic5 -x ../Windows/UI_files/PerfOptions.ui -o ../Windows/Templates/PerfOptionsTemplate.py
	pyuic5 -x ../Windows/UI_files/SimplePerfOptions.ui -o ../Windows/Templates/SimplePerfOptionsTemplate.py
	pyuic5 -x ../Windows/UI_files/Select.ui -o ../Windows/Templates/SelectTemplate.py

cython:
	python3 ../cython_modules/ex_setup.py build_ext --build-lib ../cython_modules/ --inplace
del:
	cd ../
	rm -rf build
	rm -rf cython_modules/build
	rm -rf cython_modules/*.c
	rm -rf *.so
