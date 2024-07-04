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
import json
from tqdm import tqdm
from requests.exceptions import RequestException


# # Define the WebScraper class
class WebScraper:
    def __init__(self, 
                 url='https://www.ebay.co.uk/sch/i.html?_fsrp=1&_from=R40&_nkw=laptop+computer&_sacat=0&_sop=12&LH_PrefLoc=2&_oaa=1&_dcat=177&LH_BIN=1&LH_Sold=1&LH_Complete=1&rt=nc&LH_ItemCondition=1500%7C2010%7C2020%7C2030%7C3000%7C1000', 
                 file_path=None, 
                 product_type=None, 
                 exclude_brand=None):
        self.url = url
        self.file_path = file_path
        self.product_type = product_type
        self.exclude_brand = exclude_brand

    # Function to generate list of models to scrape for a given product type
    def generate_query_list(self):
        # Read the CSV file into a Pandas DataFrame
        df = pd.read_csv(self.file_path)

        # Designate Product Type to filter
        filter = self.product_type

        # Drop rows that do not contain the filter in the 'Product Type' column
        df = df[df['ProductType'].str.contains(filter, na=False)]

        # Convert the 'Model' column to a string
        df['Model'] = df['Model'].astype(str)

        # Create a list of unique entries in the 'Model' column
        model_list = df['Model'].unique().tolist()

        # Add the 'Manufacturer' entry to the beginning of each string in the list
        manufacturer_model_list = [df.loc[df['Model'] == model, 'Manufacturer'].fillna('').iloc[0] + ' ' + model for model in model_list if self.exclude_brand not in model]

        # Remove any string that contains the word of the excluded manufacturer
        query_list = [string for string in manufacturer_model_list if self.exclude_brand not in string]

        # Lowercase all strings in the list
        query_list = [string.lower() for string in query_list]

        # Replace any spaces in the strings with a plus sign
        query_list = [string.replace(' ', '+') for string in query_list]

        return query_list

    # Function to load cookies from a json file
    def load_cookies(self, file_path):
        # Load cookies from json
        with open(file_path) as f:
            cookies = json.load(f)

        # Make a GET request to fetch the raw HTML content using the cookies provided in the dictionary above
        html_content = requests.get(self.url, cookies=cookies)

        for cookie in html_content.cookies:
            print('cookie domain = ' + cookie.domain)
            print('cookie name = ' + cookie.name)
            print('cookie value = ' + cookie.value)
            print('*************************************')

        html_content = requests.get(self.url, cookies=cookies).text
        # Parse the html content
        soup = BeautifulSoup(html_content, "lxml")
        print(soup.prettify()) # print the parsed data of html

        return cookies     

    # Function to get the BeautifulSoup object for a given URL
    def get_page(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.text, 'lxml')
        if not response.ok:
            print('Server responded:', response.status_code)
        else:
            soup = BeautifulSoup(response.text, 'lxml')
        return soup

    # Function to extract product data from a BeautifulSoup object
    def get_products(self, soup):
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
    def get_index_data(self, soup):
        try:
            links = soup.find_all('a', class_='s-item__link')
        except:
            links = []
            
        urls = [item.get('href') for item in links]
        return urls

    # Function to extract specific data from a file
    def search_nested_classes(self, file, search_words, lnln):
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
            return specifics

    # Function to extract the sold date and item number of a product
    def get_ID_sold_date(self, url, cookies, search):
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
        
        # Check if folder exists, if not, create it
        folder = 'csv/SoldDates'
        if not os.path.exists(folder):
            os.makedirs(folder)    

        # Write the DataFrame to a CSV file
        df.to_csv(f'csv/SoldDates/{search}_output_SoldDate.csv', index=False)

        return df

    # Function to load most recent csv file
    def load_most_recent_csv(self, folder_path):
        # Get a list of all CSV files in the folder
        csv_files = glob.glob(os.path.join(folder_path, '*.csv'))

        # Get the most recent CSV file
        most_recent_file = max(csv_files, key=os.path.getctime)

        # Read the data from the most recent CSV file
        df = pd.read_csv(most_recent_file)

        # Lowercase the column names
        df.columns = df.columns.str.lower()

        # Lowercase all entries
        df = df.applymap(lambda s: s.lower() if type(s) == str else s)

        return df

    # Function to merge all csv files into one
    def merge_csv_files(self, folder_path, output_path):
        all_filenames = [i for i in glob.glob(os.path.join(folder_path, '*.csv'))]
        if not all_filenames:
            print("all_filenames is empty")
            return
        dataframes = []
        for f in all_filenames:
            if os.path.getsize(f) > 0:
                try:
                    print(f"Reading file: {f}")
                    df = pd.read_csv(f, skiprows=1)
                    dataframes.append(df)
                except pd.errors.EmptyDataError:
                    print(f"File {f} is empty. Skipping...")
                except Exception as e:
                    print(f"An error occurred: {e}")
                    continue
        if not dataframes:
            print("dataframes is empty")
            return
        combined_csv = pd.concat(dataframes)
        os.makedirs('complete', exist_ok=True)
        combined_csv.columns = ['sold_date', 'item_number']
        combined_csv.to_csv(output_path, index=False, encoding='utf-8-sig')
        return pd.read_csv(output_path)

    # Function to combine and align csv files
    def combine_and_align(self, folder_path, sold_dates_path):
        df = self.load_most_recent_csv(folder_path)
        sold_dates_combined = pd.read_csv(sold_dates_path)
        sold_dates_combined = sold_dates_combined.dropna(how='all')
        sold_dates_combined.rename(columns={'item_number': 'item number'}, inplace=True)
        df2 = pd.merge(df, sold_dates_combined, on='item number', how='left')
        duplicates = df2[df2.duplicated()]
        print(f'The merged dataframe contains {len(duplicates)} duplicate rows.')
        df2.drop_duplicates(inplace=True)
        print(f'The cleaned dataframe contains {len(df2)} rows.')
        missing_values = df2.isnull().sum()
        print(missing_values)
        # Check if folder exists, if not, create it
        folder = 'dataset//update'
        if not os.path.exists(folder):
            os.makedirs(folder)
        df2.to_csv(f"{folder}/update_pre_clean.csv", index=False)


    # Main function to scrape eBay product data
    def run(self, query_list_source, num_queries=None, num_results=None, num_products=None, randomize_queries=True, query_fraction=None):

        # Load cookies from a json file
        cookies = self.load_cookies('credentials//cookies.json')

        # Start timer to measure the time taken to scrape the data
        start_time = time.time()

        query_list = self.generate_query_list(query_list_source, self.product_type, self.exclude_brand)
        print(len(query_list))

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
                products = self.get_index_data(self.get_page(url + '&_pgn={}'.format(page)))
                # If num_products is None, process all products. Otherwise, process the first num_products products.
                products_to_process = products if num_products is None else products[:num_products]

                for lnln in tqdm(products_to_process, desc="Processing products", unit="product"):

                    # Get the ID and sold date of the product
                    self.get_ID_sold_date(url + '&_pgn={}'.format(page), cookies, search)


                    # Save the HTML content of the product page to a file
                    filename = f'html_files/temp.html'
                    folder = os.path.dirname(filename)
                    # Check if the folder exists, if not, create it
                    if not os.path.exists(folder):
                        os.makedirs(folder)
                    response = requests.get(lnln)
                    if response.ok:
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(response.text)
                        #print(f'Saved {filename}')
                    else:
                        print(f'Server responded with {response.status_code}')

                    # Extract the product data from the page
                    Prod_data = self.get_products(self.get_page(lnln))
                    #print(Prod_data)

                    # Extract the specific data from the HTML content of the file
                    try:
                        item_specifics = self.search_nested_classes(filename, search_words, lnln)
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
            

            # Check if folder exists, if not, create it
            folder = 'csv/ProductData'
            if not os.path.exists(folder):
                os.makedirs(folder)

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

        # Load csv to dataframe
        df = self.load_most_recent_csv('csv//ProductData')
        print(df)

        # Merge SoldDate csv files
        sold_dates_combined = self.merge_csv_files("csv//SoldDates", 'temp//sold_dates_combined.csv')
        print(sold_dates_combined)

        # Combine and align csv files
        self.combine_and_align('ProductData', 'temp//sold_dates_combined.csv', 'dataset//update//update_pre_clean.csv')


if __name__ == "__main__":
    scraper = WebScraper()
    scraper.run(
        query_list_source="source_csv//products.csv",
        num_queries=10,
        num_results=100,
        num_products=50,
        randomize_queries=True,
        query_fraction=0.1
    )





