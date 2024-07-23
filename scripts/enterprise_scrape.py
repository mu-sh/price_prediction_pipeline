# Enterprise webscraping test script


# Import libraries
from webscraper_class import WebScraper
import pandas as pd

# Load csv as df
df = pd.read_csv('source_csv/enterprise_inventory.csv')


# Rename first column to 'product_type
df.rename(columns={df.columns[0]: 'ProductType'}, inplace=True)
df.rename(columns={df.columns[1]: 'Manufacturer'}, inplace=True)


# Save to csv
df.to_csv('source_csv/enterprise_inventory.csv', index=False)


# Check df info
df.head()
print(df['ProductType'].unique())
print(df['ProductType'].value_counts())


# Set loop to save each product type to a new df 
for product in df['ProductType']:
    

    scraper = WebScraper(product_type= product, exclude_brand='APPLE', extra_search_params=None)
    scraper.run(
    query_list_source="source_csv/enterprise_inventory.csv",
    num_queries=None,
    num_results=None,
    num_products=None,
    randomize_queries=False,
    query_fraction=None,
    )

    scraper.save_data('output_csv//enterprise.csv')
