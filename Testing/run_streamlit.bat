@echo off
echo Starting Data Analysis Dashboard...
echo.
echo Installing dependencies...
pip install -r streamlit_requirements.txt
echo.
echo Starting Streamlit application...
echo The dashboard will open in your browser at http://localhost:8501
echo.
echo Press Ctrl+C to stop the application
echo.
streamlit run streamlit_app.py
pause
