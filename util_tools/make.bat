set PYUIC_PATH=C:\Users\Jakub\AppData\Local\Programs\Python\Python36\Scripts\pyuic5.exe
set UI_PATH=../Windows/UI_files/
set TEMPLATE_PATH=../Windows/Templates/
%PYUIC_PATH% -x %UI_PATH%MainWindow.ui -o %TEMPLATE_PATH%MainWindowTemplate.py
%PYUIC_PATH% -x %UI_PATH%animationSettings.ui -o %TEMPLATE_PATH%animationSettingsTemplate.py
%PYUIC_PATH% -x %UI_PATH%PlotSettings.ui -o %TEMPLATE_PATH%PlotSettingsTemplate.py
%PYUIC_PATH% -x %UI_PATH%PerfOptions.ui -o %TEMPLATE_PATH%PerfOptionsTemplate.py
%PYUIC_PATH% -x %UI_PATH%SimplePerfOptions.ui -o %TEMPLATE_PATH%SimplePerfOptionsTemplate.py
%PYUIC_PATH% -x %UI_PATH%Select.ui -o %TEMPLATE_PATH%SelectTemplate.py
%PYUIC_PATH% -x %UI_PATH%ArrowPerfOptions.ui -o %TEMPLATE_PATH%ArrowPerfOptionsTemplate.py
