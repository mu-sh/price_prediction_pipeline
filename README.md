# Webscraper.py

## Overview
`webscraper.py` is a Python script designed to scrape eBay product data using BeautifulSoup. It is intended for educational purposes or to assist in gathering product information where permitted by eBay's terms of service.

## Features
- Utilizes BeautifulSoup for parsing HTML.
- Employs `requests` for making HTTP requests to eBay.
- Saves scraped data into CSV format using Python's `csv` module.
- Optionally, data can be managed using `pandas` for analysis and manipulation.
- Implements delay between requests using `time` and `random` to mimic human interaction and avoid IP bans.
- Uses `cProfile` for profiling the performance of the script.

## Prerequisites
Before running `webscraper.py`, ensure you have Python installed on your system. This script was developed and tested with Python 3.10.4.

## Setting Up Your Environment
1. **Clone the Repository**
   - Clone or download the repository containing `webscraper.py` to your local machine.

2. **Create a Virtual Environment (Optional but Recommended)**
   - Navigate to the project directory in your terminal.
   - Run `python -m venv venv` to create a virtual environment named `venv`.
   - Activate the virtual environment:
     - Windows: `.\venv\Scripts\activate`
     - macOS/Linux: `source venv/bin/activate`

3. **Install Required Libraries**
   - Ensure your virtual environment is activated.
   - Install the required libraries by running `pip install requirements.txt`.

## Running the Script
- With the environment set up and activated, run the script using `python webscraper.py`.
- Ensure you are in compliance with eBay's robots.txt and terms of service before running the script.

## Note
This script is for educational purposes only. Always respect the terms of service of any website you scrape.