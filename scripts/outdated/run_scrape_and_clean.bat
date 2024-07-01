@echo off

cd /d C:\Users\jack\Documents\price_prediction_pipeline
C:\Users\jack\Documents\price_prediction_pipeline\.venv\Scripts\python.exe C:\Users\jack\Documents\price_prediction_pipeline\scripts\webscraper.py
C:\Users\jack\Documents\price_prediction_pipeline\.venv\Scripts\python.exe C:\Users\jack\Documents\price_prediction_pipeline\scripts\data_cleanup.py

timeout /t 300 /nobreak >nul