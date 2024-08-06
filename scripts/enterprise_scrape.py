# Enterprise webscraping test script


# Import libraries
from webscraper_class import WebScraper
import pandas as pd

# Create a new WebScraper object
scraper = WebScraper(product_type='switch', extra_search_params=None)
scraper.run(
query_list_source="source_csv/merged_inventory.csv",
num_queries=None,
num_results=None,
num_products=None,
randomize_queries=True,
query_fraction=None,
)


