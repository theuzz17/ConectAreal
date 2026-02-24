@echo off
REM 
python -m pip install waitress
waitress-serve --port=8000 app:app
