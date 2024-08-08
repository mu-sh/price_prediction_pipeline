# Webscraping script to scrape eBay product data using BeautifulSoup

# # Import Libraries
from bs4 import BeautifulSoup
import re
import requests
import csv
import pandas as pd
import os
import time
import glob
import time
import random
import cProfile
import pandas.errors
from tqdm import tqdm
from requests.exceptions import RequestException

# # Generate list of models to scrape for

def generate_query_list(file_path, product_filter, exclude_manufacturer):
    # Read the CSV file into a Pandas DataFrame
    df = pd.read_csv(file_path)

    # Designate Product Type to filter
    filter = product_filter

    # Drop rows that do not contain the filter in the 'Product Type' column
    df = df[df['ProductType'].str.contains(filter, na=False)]

    # Convert the 'Model' column to a string
    df['Model'] = df['Model'].astype(str)

    # Create a list of unique entries in the 'Model' column
    model_list = df['Model'].unique().tolist()

    # Add the 'Manufacturer' entry to the beginning of each string in the list
    manufacturer_model_list = [df.loc[df['Model'] == model, 'Manufacturer'].fillna('').iloc[0] + ' ' + model for model in model_list if exclude_manufacturer not in model]

    # Remove any string that contains the word of the excluded manufacturer
    query_list = [string for string in manufacturer_model_list if exclude_manufacturer not in string]

    # Lowercase all strings in the list
    query_list = [string.lower() for string in query_list]

    # Replace any spaces in the strings with a plus sign
    query_list = [string.replace(' ', '+') for string in query_list]

    return query_list


query_list = generate_query_list('csv//awb_db_complete21.03.2024.csv', 'LAPTOP', 'APPLE')
print(query_list)
print(len(query_list))



# # Webscraping cookie setup

# Set url value.
url = 'https://www.ebay.co.uk/sch/i.html?_fsrp=1&_from=R40&_nkw=laptop+computer&_sacat=0&_sop=12&LH_PrefLoc=2&_oaa=1&_dcat=177&LH_BIN=1&LH_Sold=1&LH_Complete=1&rt=nc&LH_ItemCondition=1500%7C2010%7C2020%7C2030%7C3000%7C1000'

cookies = {
    'totp': '1697125603356.90peidWcYoDZkkiIV/3fQPUbez4knEK5zaQK03p58K21UHFdLYf13eU79KEw0e/xXMY23cm0G+4EyKIeJHpBHqN3/p7Sz0gmiGjCPxcY1IvJtwTTfc2yfbb5L+9/d3FM',
    'bm_sv': 'EBC92348F7C4CB64863368F1DB5201BB~YAAQyKMQAnW1mRyLAQAADpmRJBWOVJlAigAJYqJqLk8LukHLPIkpgDKUUAJrGE+nTF2QvKPjcjayGT2dOmf2WTxCpHhOvKnHA/VovwOW39t6gLSTld0dB/+giuQBtcXM4d8exLXp6jVZSvw/gAA7eCZU8JhabIkTKTUvfAlW5v43lMT4giTl0MFTEPURxlydeNeEA6CFtumG9KbFo5Xv7QiEPQ7QFwSzaaecMqZoP/3b62TwWU/a1lum5QAnU5b2cg==~1',
    'ns1': 'BAQAAAYpI47hYAAaAANgAU2cJSGM2MDFeMTY5NzEyNTYwMDg0Nl5eMF4yfDR8MTF8NDJ8MTB8NDN8MXw3fDV8M14xXjJeNF4zXjE1XjEyXjJeMV4xXjBeMV4wXjFeNjQ0MjQ1OTA3NdpDW+IZLtFUyjZpvkOet3oa/7U5',
    'dp1': 'bu1p/QEBfX0BAX19AQA**68ea7be3^pbf/%23e000e0000000000000000067094863^bl/GB68ea7be3^',
    'ebay': '%5Ejs%3D1%5Esbf%3D%23000000%5E',
    '__uzmb': '1656403523',
    '__uzmd': '1697125601',
    '__uzma': '544f198b-f3e6-49ac-bf5f-e5d4a509b963',
    '__deba': 'TWL253FqdkWxEAf7A0bfrOUP-GqX7rG8HAGY9Z4uqFZx340qiETF8YthJ-HE8YWSDDe27C3fHLYJM-njM4OZRLTOscjqbd46jI4T43IsHDXc0JyENwjH6YlmulQvW9CGKUi4mHNVsrcllXB2uy7dNg==',
    'nonsession': 'BAQAAAYpI47hYAAaAAAgAHGVPoeMxNjc0NjM2OTU0eDExNTU3MjA3NDY2MngzeDJOADMABmcJSGNMUzMxQUEAygAgaOp74zkzMjY0NmRjMTgwMGFkYjkyNjQ1Nzc2NmZmZGUyZjVlAMsAAmUoG+s0MU0blIMzwV0GRDZjz0ShHXe1L+dh',
    '__uzmf': '7f60005b580693-943d-4ec5-9beb-b94b579ec027165640352346340722077638-48c51b9d6ef587d4982',
    'ak_bmsc': 'A552F161B4B05FDC6D81137862427FAA~000000000000000000000000000000~YAAQ0KMQAtZb2RuLAQAAbQhBJBWW8mdipJwIFRskhkFueYSuVo127yK8fakDe7H5GZq7F5+u4NP9dc3X2qtoyO8c5Q8w/JijKG8IT8pQuX37j3wuTLX3+947lRUzezUXEr+d56D4eDPXFjIrBLLlUJsr8OQcZc8Hs5E3F2OJgQH6u/NQgza2HETmGLrkyr17L7wYQQNMDeEql4aMfO9jDyyITiMv8snnoSpvN20YnWcQN5t8ny6MBeOP3o8rME4rr3Iq0gvlJdIXnwgd+Q8L7wVGWUn/wiy6WBeQiKTiJAbFzda3aXhMlZbNyw45mKsSKgnULsdmumjmSNa8HODiJqK+3II7Pe6QxB8Fpr9xmGGpZd4myv0MnHHz8LQh2gX8tWiNE+KYUSw0',
    '__uzmc': '5445098220171',
    's': 'CgADuANRlKVHDMwZodHRwczovL3d3dy5lYmF5LmNvLnVrL3NjaC9pLmh0bWw/X2ZzcnA9MSZfZnJvbT1SNDAmX25rdz1sYXB0b3AlMjBjb21wdXRlciZfc2FjYXQ9MCZMSF9QcmVmTG9jPTImX29hYT0xJl9kY2F0PTE3NyZMSF9CSU49MSZMSF9Tb2xkPTEmTEhfQ29tcGxldGU9MSZydD1uYyZMSF9JdGVtQ29uZGl0aW9uPTE1MDAlN0MyMDEwJTdDMjAyMCU3QzIwMzAlN0MzMDAwJTdDMTAwMAcA+AAgZSkxDjkzMjY0NmRjMTgwMGFkYjkyNjQ1Nzc2NmZmZGUyZjVlvEojAg**',
    '__uzme': '2607'
}

# Make a GET request to fetch the raw HTML content using the cookies provided in the dictionary above
html_content = requests.get(url, cookies=cookies)

for cookie in html_content.cookies:

    print('cookie domain = ' + cookie.domain)

    print('cookie name = ' + cookie.name)

    print('cookie value = ' + cookie.value)

    print('*************************************')

html_content = requests.get(url, cookies=cookies).text
# Parse the html content
soup = BeautifulSoup(html_content, "lxml")
print(soup.prettify()) # print the parsed data of html

cookies = {
    'totp': '1697125603356.90peidWcYoDZkkiIV/3fQPUbez4knEK5zaQK03p58K21UHFdLYf13eU79KEw0e/xXMY23cm0G+4EyKIeJHpBHqN3/p7Sz0gmiGjCPxcY1IvJtwTTfc2yfbb5L+9/d3FM',
    'bm_sv': 'EBC92348F7C4CB64863368F1DB5201BB~YAAQyKMQAnW1mRyLAQAADpmRJBWOVJlAigAJYqJqLk8LukHLPIkpgDKUUAJrGE+nTF2QvKPjcjayGT2dOmf2WTxCpHhOvKnHA/VovwOW39t6gLSTld0dB/+giuQBtcXM4d8exLXp6jVZSvw/gAA7eCZU8JhabIkTKTUvfAlW5v43lMT4giTl0MFTEPURxlydeNeEA6CFtumG9KbFo5Xv7QiEPQ7QFwSzaaecMqZoP/3b62TwWU/a1lum5QAnU5b2cg==~1',
    'ns1': 'BAQAAAYpI47hYAAaAANgAU2cJSGM2MDFeMTY5NzEyNTYwMDg0Nl5eMF4yfDR8MTF8NDJ8MTB8NDN8MXw3fDV8M14xXjJeNF4zXjE1XjEyXjJeMV4xXjBeMV4wXjFeNjQ0MjQ1OTA3NdpDW+IZLtFUyjZpvkOet3oa/7U5',
    'dp1': 'bu1p/QEBfX0BAX19AQA**68ea7be3^pbf/%23e000e0000000000000000067094863^bl/GB68ea7be3^',
    'ebay': '%5Ejs%3D1%5Esbf%3D%23000000%5E',
    '__uzmb': '1656403523',
    '__uzmd': '1697125601',
    '__uzma': '544f198b-f3e6-49ac-bf5f-e5d4a509b963',
    '__deba': 'TWL253FqdkWxEAf7A0bfrOUP-GqX7rG8HAGY9Z4uqFZx340qiETF8YthJ-HE8YWSDDe27C3fHLYJM-njM4OZRLTOscjqbd46jI4T43IsHDXc0JyENwjH6YlmulQvW9CGKUi4mHNVsrcllXB2uy7dNg==',
    'nonsession': 'BAQAAAYpI47hYAAaAAAgAHGVPoeMxNjc0NjM2OTU0eDExNTU3MjA3NDY2MngzeDJOADMABmcJSGNMUzMxQUEAygAgaOp74zkzMjY0NmRjMTgwMGFkYjkyNjQ1Nzc2NmZmZGUyZjVlAMsAAmUoG+s0MU0blIMzwV0GRDZjz0ShHXe1L+dh',
    '__uzmf': '7f60005b580693-943d-4ec5-9beb-b94b579ec027165640352346340722077638-48c51b9d6ef587d4982',
    'ak_bmsc': 'A552F161B4B05FDC6D81137862427FAA~000000000000000000000000000000~YAAQ0KMQAtZb2RuLAQAAbQhBJBWW8mdipJwIFRskhkFueYSuVo127yK8fakDe7H5GZq7F5+u4NP9dc3X2qtoyO8c5Q8w/JijKG8IT8pQuX37j3wuTLX3+947lRUzezUXEr+d56D4eDPXFjIrBLLlUJsr8OQcZc8Hs5E3F2OJgQH6u/NQgza2HETmGLrkyr17L7wYQQNMDeEql4aMfO9jDyyITiMv8snnoSpvN20YnWcQN5t8ny6MBeOP3o8rME4rr3Iq0gvlJdIXnwgd+Q8L7wVGWUn/wiy6WBeQiKTiJAbFzda3aXhMlZbNyw45mKsSKgnULsdmumjmSNa8HODiJqK+3II7Pe6QxB8Fpr9xmGGpZd4myv0MnHHz8LQh2gX8tWiNE+KYUSw0',
    '__uzmc': '5445098220171',
    's': 'CgADuANRlKVHDMwZodHRwczovL3d3dy5lYmF5LmNvLnVrL3NjaC9pLmh0bWw/X2ZzcnA9MSZfZnJvbT1SNDAmX25rdz1sYXB0b3AlMjBjb21wdXRlciZfc2FjYXQ9MCZMSF9QcmVmTG9jPTImX29hYT0xJl9kY2F0PTE3NyZMSF9CSU49MSZMSF9Tb2xkPTEmTEhfQ29tcGxldGU9MSZydD1uYyZMSF9JdGVtQ29uZGl0aW9uPTE1MDAlN0MyMDEwJTdDMjAyMCU3QzIwMzAlN0MzMDAwJTdDMTAwMAcA+AAgZSkxDjkzMjY0NmRjMTgwMGFkYjkyNjQ1Nzc2NmZmZGUyZjVlvEojAg**',
    '__uzme': '2607'
}


## Webscraping functions

# Function to get the BeautifulSoup object for a given URL
def get_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    if not response.ok:
        print('Server responded:',response.status_code)
    else:
        soup = BeautifulSoup(response.text, 'lxml')
    return soup

# Function to extract product data from a BeautifulSoup object
def get_products(soup):
    try:
        title = soup.find('h1', {'class': 'x-item-title__mainTitle'}).find('span').text 
    except:
        title = ''
    try:
        processor = soup.find('h1', {'class': 'x-item-title__mainTitle'}).find('span').text 
    except:
        processor = ''
    try:
        Original_price = soup.find('div', {'class': 'x-bin-price__content'}).find('span').text.strip()
        OrgCurrency, Orgprice = Original_price.split(' ')
    except:
        OrgCurrency = ''
        Orgprice = ''
    try:
        Starting_bid = soup.find('span', {'itemprop': 'price'}).find('span').text.strip()
        Currency, price = Starting_bid.split(' ')
    except:
        Currency = ''
        price = ''
    try:
        quantity_availability = soup.find('div', {'class': 'd-quantity__availability'}).find('span').find('class').text.strip().split(' ')[0]
    except:
        quantity_availability = ''
    try:
        condition = soup.find('span', {'data-testid': 'ux-textual-display'}).find('span').text 
    except:
        condition = ''


    # Return a dictionary containing the extracted data
    data = {
        'Title': title,
        'Original_price': Orgprice,
        'OrgCurrency': OrgCurrency,
        'Starting_bid': price,
        'Currency': Currency,
        'Quantity_availability': quantity_availability,
        'Condition': condition
    }
    return data

# Function to extract product links from a BeautifulSoup object
def get_index_data(soup):
    try:
        links = soup.find_all('a', class_='s-item__link')
    except:
        links = []
        
    urls = [item.get('href') for item in links]
    return urls

# Function to write product data to a CSV file
def write_csv(Prod_data, lnln):
    with open('33EbayProduct.csv', 'a', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        row = [Prod_data['Title'], Prod_data['Original_price'], Prod_data['OrgCurrency'], Prod_data['Starting_bid'], Prod_data['Currency'], Prod_data['Quantity_availability'], Prod_data['Condition'], lnln]
        writer.writerow(row)

# Function to extract specific data from a file
def search_nested_classes(file, search_words, lnln):
    with open(file, encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
        price_span = soup.select_one('div.x-price-primary span.ux-textspans')
        if price_span is not None:
            price_text = price_span.text.strip()
            price_value = re.sub('[^0-9\.]', '', price_text)
        else:
            price_value = None   
        nested_classes = soup.select('div.ux-layout-section-evo__item--table-view span.ux-textspans')
        specifics = {}
        specifics.update({'Price' : price_value})
        link = {'Link': lnln}
        title_span = soup.find('h1', {'class': 'x-item-title__mainTitle'})
        if title_span is not None:
            title = title_span.find('span').text
        else:
            title = None
         
        specifics.update({'Title' : title})
        
        item_number = soup.find('div', {'class': 'ux-layout-section__textual-display ux-layout-section__textual-display--itemId'})
        if item_number is not None:
            item_number = item_number.find_all('span')[1].text
        else:
            item_number = None


        specifics.update({'Item Number' : item_number})
        specifics.update(link)
        for i in range(len(nested_classes)):
            for word in search_words:
                if re.search('^' + word + '$', nested_classes[i].text):
                    next_class = nested_classes[i+1]
                    specifics[word] = next_class.text
                    break
        #print(specifics)        
        return specifics

def get_ID_sold_date(url, cookies, search):
    # Send a GET request to the URL
    response = requests.get(url, cookies=cookies)

    # Parse the HTML content of the page using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all the products on the page
    products = soup.find_all('div', {'class': 's-item__wrapper'})

    # Define an empty list to store the data
    data = []

    # Loop through each product on the page
    for product in products:
        # Extract the sold date and item number
        try:
            sold_date = product.find('div', {'class': 's-item__title--tag'}).find('span').text.split('Sold ')[1] 
        except:
            sold_date = ''
        try:
            item_number = product.find('span', {'class': 's-item__item-id'}).text.split(': ')[1]
        except:
            item_number = ''

        # Append the data to the list
        data.append({'sold_date': sold_date, 'item_number': item_number})

    # Create a dataframe from the data
    df = pd.DataFrame(data)

    # Convert the 'Sold Date' column to a datetime format
    try:
        df['sold_date'] = pd.to_datetime(df['sold_date'])
    except:
        pass
    
    # Write the DataFrame to a CSV file
    df.to_csv(f'csv/SoldDates/{search}_output_SoldDate.csv', index=False)

    return df


# Main function to scrape eBay product data
def main(num_queries=None, num_results=None, num_products=None, randomize_queries=True, query_fraction=None):
    # Start timer to measure the time taken to scrape the data
    start_time = time.time()

    # Initialize query list
    queries_to_scrape = query_list 

    # Randomize the order of the queries if requested
    if randomize_queries:
        random.shuffle(queries_to_scrape)

    # If num_queries is None and query_fraction is not None, calculate the number of queries to scrape based on the query_fraction
    if num_queries is None and query_fraction is not None:
        num_queries = int(len(queries_to_scrape) / query_fraction)

    # If num_queries is None, scrape all queries. Otherwise, scrape the first num_queries queries.
    queries_to_scrape = queries_to_scrape if num_queries is None else queries_to_scrape[:num_queries]

    print(f'Scraping {len(queries_to_scrape)} queries') 

    # Initialize rows list outside the loop
    rows = []


    for query in tqdm(queries_to_scrape, desc="Processing queries", unit="query"):
        # Set the search term and the URL for buy it now listings
        search = f'{query}+laptop+computer'
        sold_url = f'https://www.ebay.co.uk/sch/i.html?_fsrp=1&_from=R40&_nkw={search}&_sacat=0&_sop=12&LH_PrefLoc=2&_oaa=1&_dcat=177&LH_BIN=1&LH_Sold=1&LH_Complete=1&rt=nc&LH_ItemCondition=1500%7C2010%7C2020%7C2030%7C3000%7C1000'
        url = sold_url

        # Read the list of search words from a text file
        with open('scripts//ItemSpecifics.txt', 'r') as f:
            search_words = f.read().splitlines()

        # If num_results is None, scrape all results. Otherwise, scrape the first num_results results.
        results_to_scrape = range(1, 2) if num_results is None else range(1, num_results + 1)
        print(query)
        # Loop through the pages of search results
        for page in tqdm(results_to_scrape, desc="Processing pages", unit="page"):
            
            

            # Extract the product links from the page
            products = get_index_data(get_page(url + '&_pgn={}'.format(page)))
            # If num_products is None, process all products. Otherwise, process the first num_products products.
            products_to_process = products if num_products is None else products[:num_products]

            for lnln in tqdm(products_to_process, desc="Processing products", unit="product"):

                # Get the ID and sold date of the product
                get_ID_sold_date(url + '&_pgn={}'.format(page), cookies, search)


                # Save the HTML content of the product page to a file
                filename = f'html_files/temp.html'
                response = requests.get(lnln)
                if response.ok:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    #print(f'Saved {filename}')
                else:
                    print(f'Server responded with {response.status_code}')

                # Extract the product data from the page
                Prod_data = get_products(get_page(lnln))
                #print(Prod_data)

                # Extract the specific data from the HTML content of the file
                try:
                    item_specifics = search_nested_classes(filename, search_words, lnln)
                except FileNotFoundError:
                    print(f'{filename} not found')
                    continue
                
                # Append the specific data to a list of rows
                rows.append(item_specifics)

                # Delete the file
                if os.path.exists(filename):
                    os.remove(filename)
                    #print(f'{filename} deleted successfully')
                else:
                    print(f'{filename} does not exist')
                
        # Create a pandas DataFrame from the list of rows
        df = pd.DataFrame(rows)
        
        # Check if the columns exist in the DataFrame before selecting them
        cols = ['Price' , 'Item Number', 'Brand','Model', 'Series','Condition', 'Processor'
                ,'Processor Speed','RAM Size','GPU','Type', 'Graphics Processing Type','Operating System', 'Storage Type',
                'Screen Size','Features', 'Seller notes', 'Title', 'Link']
        for col in ['Maximum Resolution', 'HDD Capacity', 'SSD Capacity']:
            if col in df.columns:
                cols.append(col)
        df = df[cols]
        
        # Write the DataFrame to a CSV file and display it
        df.to_csv(f'csv/ProductData/{search}_output_.csv', index=False)
        #display(df)
        
        print(f'{query} Scraped Successfully')

        # Print the time taken to scrape the data
        print(f'Time taken to scrape the data: {time.time() - start_time} seconds')

        # Calculate an estimate of time remaining to scrape the entire query list
        time_remaining = (time.time() - start_time) * (len(query_list) / (query_list.index(query) + 1) - 1)
        # Convert time remaining from seconds to hours and minutes
        time_remaining = str(round(time_remaining / 3600)) + ' hours and ' + str(round((time_remaining % 3600) / 60)) + ' minutes'
        
        print(f'Estimated time remaining: {time_remaining}')

# Run the main function       
rows = []
main()




# ## Load csv to dataframe

folder_path = 'csv//ProductData'

# Get a list of all CSV files in the folder
csv_files = glob.glob(os.path.join(folder_path, '*.csv'))

# Get the most recent CSV file
most_recent_file = max(csv_files, key=os.path.getctime)

# Read the data from the most recent CSV file
df = pd.read_csv(most_recent_file)

# Lowercase the column names
df.columns = df.columns.str.lower()

# Lowercase all entries
df = df.applymap(lambda s:s.lower() if type(s) == str else s)

print(df)


# ## Merge SoldDate csv files

# Merge all csv files into one
os.chdir("csv//SoldDates")
extension = 'csv'
all_filenames = [i for i in glob.glob('*.{}'.format(extension))]

# Check if all_filenames is empty
if not all_filenames:
    print("all_filenames is empty")

# Combine all files in the list
dataframes = []  # List to store DataFrames
for f in all_filenames:
    if os.path.getsize(f) > 0:  # Check if file is not empty
        try:
            print(f"Reading file: {f}")  # Print file name
            df = pd.read_csv(f, skiprows=1)  # Read file
            dataframes.append(df)  # Append DataFrame to list
        except pandas.errors.EmptyDataError:
            print(f"File {f} is empty. Skipping...")
        except Exception as e:
            print(f"An error occurred: {e}")
            continue

# Check if dataframes is empty
if not dataframes:
    print("dataframes is empty")
else:
    combined_csv = pd.concat(dataframes)  # Concatenate all DataFrames

print(f"Current directory before: {os.getcwd()}")
os.chdir("..")
print(f"Current directory after: {os.getcwd()}")
# Ensure the directory exists
os.makedirs('complete', exist_ok=True)

# Name columns
combined_csv.columns = ['sold_date', 'item_number']

#export to csv
combined_csv.to_csv('temp//sold_dates_combined.csv', index=False, encoding='utf-8-sig')

# Read the data from the CSV file
sold_dates_combined = pd.read_csv('temp//sold_dates_combined.csv')

# Remove empty rows
sold_dates_combined = sold_dates_combined.dropna(how='all')

# Display the updated DataFrame
print(sold_dates_combined)



# ## Combine and align csv files

# Align and add combined csv file to the main csv file, by Item Number

# Read the data from the most recent CSV file
# Set the path to the folder containing the CSV files
folder_path = 'ProductData'

print(f"Folder path: {folder_path}")

# Get a list of all CSV files in the folder
csv_files = glob.glob(os.path.join(folder_path, '*.csv'))

print(f"CSV files: {csv_files}")

# Get the most recent CSV file
most_recent_file = max(csv_files, key=os.path.getctime)

# Read the data from the most recent CSV file
df = pd.read_csv(most_recent_file)

# Lowercase the column names
df.columns = df.columns.str.lower()

# Lowercase all entries
df = df.applymap(lambda s:s.lower() if type(s) == str else s)

#  Rename item_number column to Item Number
sold_dates_combined.rename(columns={'item_number': 'item number'}, inplace=True)

# Merge the dataframes on the 'item number' column
df2 = pd.merge(df, sold_dates_combined, on='item number', how='left')

# Write the DataFrame to a CSV file and display it
df2.to_csv(f'temp//AlignedComplete.csv', index=False)

# Check for duplicate rows in the merged dataframe
duplicates = df2[df2.duplicated()]

# Print the number of duplicate rows
print(f'The merged dataframe contains {len(duplicates)} duplicate rows.')

# Remove duplicate rows from the merged dataframe
df2.drop_duplicates(inplace=True)

# Print the number of rows in the cleaned dataframe
print(f'The cleaned dataframe contains {len(df2)} rows.')

# Check for missing values in the merged dataframe
missing_values = df2.isnull().sum()

# Print the number of missing values for each column
print(missing_values)

# Change directory
os.chdir("..")

# Write the DataFrame to a CSV file and display it
df2.to_csv(f'dataset//update//update_pre_clean.csv', index=False)


