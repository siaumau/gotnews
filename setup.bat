@echo off
echo Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo Setup complete!
echo.
echo Please set NewsAPI key:
echo set NEWS_API_KEY=your_api_key_here
echo.
echo Then run:
echo python app.py
pause