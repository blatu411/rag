@echo off
echo Starting DeepSeek AI Chat + RAG Application...
echo.
set PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
python -m streamlit run app.py
pause
