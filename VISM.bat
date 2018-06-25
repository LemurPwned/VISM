@echo off
@echo Launching VISM ...
@echo.


set PYTHON_INST=
for %%e in (%PATHEXT%) do (
  for %%X in (python%%e) do (
    if not defined PYTHON_INST (
      set PYTHON_INST=%%~$PATH:X
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


@echo Building cython modules...
CD cython_modules
@echo on
%PYTHON_INST% setup.py build_ext --inplace
@echo off
CD ..
@echo.
%PYTHON_INST% main.py
PAUSE
