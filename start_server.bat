@echo off
echo Starting Questionnaire Management System...
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Start the backend server
echo Starting backend server...
echo Open your browser and go to: http://localhost:5000/admin
echo.
echo Press Ctrl+C to stop the server
echo.

python backend/app.py

pause