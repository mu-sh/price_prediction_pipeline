# Webscraper.py

## Overview
`webscraper.py` is a Python script designed to scrape eBay product data using BeautifulSoup. It is intended for educational purposes or to assist in gathering product information where permitted by eBay's terms of service.
`data_cleanup.py` is then run to clean the resulting scraped data ready for EDA
 

## Features
- Utilizes BeautifulSoup for parsing HTML.
- Employs `requests` for making HTTP requests to eBay.
- Saves scraped data into CSV format using Python's `csv` module.
- Optionally, data can be managed using `pandas` for analysis and manipulation.
- Implements delay between requests using `time` and `random` to mimic human interaction and avoid IP bans.
- Uses `cProfile` for profiling the performance of the script.

## Prerequisites

1. **Install Python**
   - Before running `webscraper.py`, ensure you have Python installed on your system. This script was developed and tested with Python 3.10.4.

2. **Export browser cookies**
   - Open a new browser window
   - Navigate to eBay homepage
 
   For Google Chrome:
     1. Open Developer Tools:
         - Press F12 or Ctrl+Shift+I to open Developer Tools.
         - Alternatively, you can right-click on the page and select "Inspect".

     2. Go to the Application Tab:
         - In Developer Tools, navigate to the "Application" tab.

     3. Locate Cookies:
         - In the left sidebar, under "Storage", click on "Cookies".
         - Select the URL for which you want to export cookies.

     4. Export Cookies:
         - Right-click on the cookies table and select "Export".
         - Save the file as cookies.json.  

   For Mozilla Firefox:
     1. Open Developer Tools:
         - Press F12 or Ctrl+Shift+I to open Developer Tools.
         - Alternatively, you can right-click on the page and select "Inspect Element".

     2. Go to the Storage Tab:
         - In Developer Tools, navigate to the "Storage" tab.

     3. Locate Cookies:
         - In the left sidebar, expand "Cookies" and select the URL for which you want to export cookies.

     4. Export Cookies:
         - Right-click on the cookies table and select "Export All".
         - Save the file as cookies.json.


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

## Using the class
### Parameters for `WebScraper.run`

The `WebScraper.run` method is used to scrape product data from eBay. Below are the descriptions of the parameters you need to provide:

- **`query_list_source`**: The path to the CSV file containing the list of queries to be used for scraping. For example, `"source_csv//products.csv"`.

- **`product_type`**: The type of product you want to scrape. This is a string value, such as `"LAPTOP"`.

- **`exclude_brand`**: The brand you want to exclude from the scraping results. This is a string value, such as `"APPLE"`.

- **`num_queries`**: The number of queries to be used for scraping. This is an integer value. For example, `10`.

- **`num_results`**: The number of results to be fetched per query. This is an integer value. For example, `100`.

- **`num_products`**: The total number of products to be scraped. This is an integer value. For example, `50`.

- **`randomize_queries`**: A boolean value indicating whether to randomize the order of the queries. For example, `True`.

- **`query_fraction`**: A fraction of the total queries to be used for scraping. This is a float value. For example, `0.1`.

### Example Usage

```python
scraper.run(
    query_list_source="source_csv//products.csv",
    product_type="LAPTOP",
    exclude_brand="APPLE",
    num_queries=10,
    num_results=100,
    num_products=50,
    randomize_queries=True,
    query_fraction=0.1
)
