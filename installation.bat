@echo off
@echo Installation begins...
@echo.

@echo Checking Python Installation...
@echo Looking for python in the path...
@echo.
set PYTHON_INST=
for %%e in (%PATHEXT%) do (
  for %%X in (python%%e) do (
    if not defined PYTHON_INST (
      set PYTHON_INST=%%~$PATH:X
    )
  )
)
set PIP_INST=
for %%e in (%PATHEXT%) do (
  for %%X in (pip%%e) do (
    if not defined PIP_INST (
      set PIP_INST=%%~$PATH:X
    )
  )
)
if not defined PYTHON_INST (
	@echo Python installation not found...
	@echo Install python and put it into the path
	) else (
	@echo Installation found at: ...
	@echo %PYTHON_INST%
)
@echo.
if not defined PIP_INST (
	@echo PIP installation not found...
	@echo Install python and put it into the path
	) else (
	@echo Installation found at: ...
	@echo %PIP_INST%
)
@echo.
@echo on

@echo Installing requirements for the VISM software...
%PIP_INST% install -r requirements.txt

@echo Building cython modules...
CD cython_modules
%PYTHON_INST% setup.py build_ext --inplace
@echo off
@echo.
@echo If above has not failed then you can run VISM now!
@echo Otherwise install proper VCC or GCC build tools like Visual Studio VCC+ from here:
@echo https://www.visualstudio.com/downloads/#build-tools-for-visual-studio-2017
PAUSE