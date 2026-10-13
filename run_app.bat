
@echo off
REM Set the project root so Python can import the app package.
set "PYTHONPATH=%~dp0"

REM Start the Streamlit application using uv.
uv run streamlit run app/streamlit_app.py

pause
