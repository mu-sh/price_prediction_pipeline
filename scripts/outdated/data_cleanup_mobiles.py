# # Data cleaning script to clean the scraped data 

# ## Import libraries
import re
import pandas as pd
import os
from datetime import datetime
from datasetupdater import update_dataset
from rapidfuzz import process, fuzz


import sys
sys.path.insert(0, 'C://Users//jack//Documents//aiken_upload_pipeline//Python_scripts')
from Export_Functions import gsheets_connect

# Get current date
current_date = datetime.now().strftime('%Y-%m-%d')


# Read the data from the CSV file
df = pd.read_csv('dataset//update//update_pre_clean.csv')

# Drop duplicate rows
df.drop_duplicates(inplace=True)

# Drop rows with missing 'Price' values
df.dropna(subset=['price'], inplace=True)

print(df)



# ## Remove job lot listings
# Drop rows with 'Job lot' in the 'Title', 'Seller notes', or 'Condition' column
df = df[~df['title'].str.contains('job lot')]
df['seller notes'] = df['seller notes'].fillna('')
df = df[~df['seller notes'].str.contains('job lot')]
df['condition'] = df['condition'].astype(str) # Convert to string
df = df[~df['condition'].str.contains('job lot')]

# Drop rows with 'faulty' in the 'Title', 'Seller notes', or 'Condition' column
df = df[~df['title'].str.contains('faulty')]
df = df[~df['seller notes'].str.contains('faulty')]
df['condition'] = df['condition'].astype(str) # Convert to string
df = df[~df['condition'].str.contains('faulty')]

# Drop rows with 'spares' in the 'Title', 'Seller notes', or 'Condition' column
df = df[~df['title'].str.contains('spares')]
df = df[~df['seller notes'].str.contains('spares')]
df['condition'] = df['condition'].astype(str) # Convert to string
df = df[~df['condition'].str.contains('spares')]

# Drop rows with 'any' or 'various' or 'depends on stock' in the 'model' column
df['model'] = df['model'].fillna('')
df = df[~df['model'].str.contains('any')]
df = df[~df['model'].str.contains('various')]
df = df[~df['model'].str.contains('depends on stock')]

# Drop rows with '/' in the 'brand' or 'model' column
df['brand'] = df['brand'].fillna('')
df = df[~df['brand'].str.contains('/')]
df = df[~df['model'].str.contains('/')]

print(df)

# ## Remove none working devices

# Drop all entries which don't contain 'Good', 'Used', 'New', 'Excellent' or 'Refurbished' in the Condition column
df = df[df['condition'].str.contains('good|used|new|excellent|refurbished')]
print(df)

# ## CPU generation splitter

# Split Processor column into Processor i series and Processor generation columns
df['processor i series'] = df['processor'].str.extract(r'(i\d+)')
df['processor generation'] = df['processor'].str.extract(r'(\d+st|\d+nd|\d+rd|\d+th|\d+st gen|\d+nd gen|\d+rd gen|\d+th gen)')

# Reorder the columns
cols = ['price', 'brand', 'processor i series', 'processor generation',
        'processor speed', 'ram size', 'ssd capacity', 'storage type', 'screen size', 'graphics processing type', 'gpu', 'operating system', 'type', 
         'model','series', 'condition', 'processor', 'features', 'seller notes', 'title', 'link','sold_date', 'item number']
df = df[cols]
df = df.rename(columns={'ssd capacity': 'storage capacity'})

# Drop rows where 'processor i series' or 'processor generation' contain NaN entries#
df.dropna(subset=['processor i series', 'processor generation'], inplace=True)

# Extract the numeric part from 'processor generation' column
df['processor generation'] = df['processor generation'].str.extract('(\d+)')

print(df)


# ## Remove 'GHz' suffix from 'Processor Speed'

# Remove 'GHz' suffix from CPU speed
df['processor speed'] = df['processor speed'].str.replace('ghz', '')

# Drop rows with NaN values in the 'processor speed' column
df.dropna(subset=['processor speed'], inplace=True)

# Drop rows with any non-float values in the 'processor speed' column
df = df[pd.to_numeric(df['processor speed'], errors='coerce').astype(float).notnull()]

# Drop rows where 'processor speed' is more than 10
df = df[df['processor speed'].astype(float) < 10]

print(df)


# ## Drop mutiple drive devices, for ease of beta test

# Drop rows with missing storage type values
df.dropna(subset=['storage type'], inplace=True)

# Drop entries which contain 'hdd + ssd' in the 'storage type' column
df = df[~df['storage type'].str.contains('\+')]
df = df[~df['storage type'].str.contains('or')]
df = df[~df['storage type'].str.contains('and')]

# List unique entries in the 'storage type' column
print(df['storage type'].unique())

# Map storage types to categories
storage_map = {'emmc': 'emmc', 'm.2 ssd': 'm.2', 'm.2 drive': 'm.2', 'nvme': 'nvme', 'ssd nvme': 'nvme', 'sshd (solid state hybrid drive)': 'sshd', 'sshd': 'sshd', 'ssd (solid state drive)': 'ssd', 'ssd': 'ssd', 'hdd (hard disk drive)': 'hdd', 'hdd': 'hdd'}
df['storage type'] = df['storage type'].str.lower().apply(lambda x: next((v for k, v in storage_map.items() if k in x), x))

print(df)


# ## Storage Capacity TB to GB conversion, remove GB suffix

# Convert TB to GB
df['storage capacity'] = df['storage capacity'].astype(str)
df['storage capacity'] = df['storage capacity'].str.replace('1tb', '1024gb')
df['storage capacity'] = df['storage capacity'].str.replace('2tb', '2048gb')
df['storage capacity'] = df['storage capacity'].str.replace('3tb', '3072gb')
df['storage capacity'] = df['storage capacity'].str.replace('4tb', '4096gb')
df['storage capacity'] = df['storage capacity'].str.replace('5tb', '5120gb')
df['storage capacity'] = df['storage capacity'].str.replace('6tb', '6144gb')
df['storage capacity'] = df['storage capacity'].str.replace('7tb', '7168gb')
df['storage capacity'] = df['storage capacity'].str.replace('8tb', '8192gb')
df['storage capacity'] = df['storage capacity'].str.replace('9tb', '9216gb')
df['storage capacity'] = df['storage capacity'].str.replace('10tb', '10240gb')
df['storage capacity'] = df['storage capacity'].str.replace('11tb', '11264gb')
df['storage capacity'] = df['storage capacity'].str.replace('12tb', '12288gb')
df['storage capacity'] = df['storage capacity'].str.replace('13tb', '13312gb')
df['storage capacity'] = df['storage capacity'].str.replace('14tb', '14336gb')
df['storage capacity'] = df['storage capacity'].str.replace('15tb', '15360gb')
df['storage capacity'] = df['storage capacity'].str.replace('16tb', '16384gb')


# Remove GB from Storage Capacity
df['storage capacity'] = df['storage capacity'].str.replace('gb', '')

# Drop rows with non numerical values in the 'storage capacity' column
df = df[pd.to_numeric(df['storage capacity'], errors='coerce').astype(float).notnull()]

# Drop rows where 'storage capacity' contains a decimal point
df = df[~df['storage capacity'].astype(str).str.contains('\.')]

# Drop rows where 'storage capacity' is less than 64
df = df[df['storage capacity'].astype(int) >= 64]

print(df)


# ## Remove GB suffix

# Remove GB from RAM size
df['ram size'] = df['ram size'].astype(str)
df['ram size'] = df['ram size'].str.replace('gb', '')

# If ram size = storage capacity, set ram size to 8gb
df.loc[df['ram size'] == df['storage capacity'], 'ram size'] = '8'

# Drop rows with non-numerical values in the 'ram size' column
df = df[pd.to_numeric(df['ram size'], errors='coerce').astype(float).notnull()]

# Drop rows where ram size is more than 64gb
df = df[df['ram size'].astype(int) <= 64]

print(df)

# # Convert screen size values

# Strip all non-numerical characters from the 'screen size' column
df['screen size'] = df['screen size'].apply(lambda x: round(float(''.join(c for c in str(x) if c.isdigit() or c == '.')), 1) if ''.join(c for c in str(x) if c.isdigit() or c == '.') and '.' in str(x) and str(x)[-1] != '.' else ''.join(c for c in str(x) if c.isdigit()))

# Drop rows with missing screen size
df = df.dropna(subset=['screen size'])

df = df[df['screen size'] != '']

# Convert screen size to float
df['screen size'] = df['screen size'].astype(float)

# Drop entries with screen size less than 10
df = df[df['screen size'] >= 10]
print(df)


# ## GPU Column cleanup

# Convert NaN entries in the 'gpu' column to 'integrated'
df['gpu'] = df['gpu'].fillna('integrated')

# Convert enties conatining 'intel' but no 'nvidia' or 'amd' to 'integrated'
df.loc[df['gpu'].str.contains('intel|integrated|hd|uhd|onboard') & ~df['gpu'].str.contains('nvidia|amd'), 'gpu'] = 'integrated'

# If entry contains '&' split string at '&' and keep the second part without the '&' symbol
df.loc[df['gpu'].str.contains('&|\+'), 'gpu'] = df['gpu'].str.split('&|\+').str[1]

# Drop 'graphics processing type' column
df.drop(columns=['graphics processing type'], inplace=True)

# If 'gpu' entry contains 'gtx' or 'radeon' but does not contain 'nvidia' or 'amd' respectively, add 'nvidia' or 'amd' to the entry
df.loc[df['gpu'].str.contains('gtx') & ~df['gpu'].str.contains('nvidia'), 'gpu'] = 'nvidia ' + df['gpu']
df.loc[df['gpu'].str.contains('radeon') & ~df['gpu'].str.contains('amd'), 'gpu'] = 'amd ' + df['gpu']

# Strip whitespace from 'gpu' column
df['gpu'] = df['gpu'].str.strip()

print(df)


# ## Remove entries with no sold date

# Drop rows with no sold date
df.dropna(subset=['sold_date'], inplace=True)

# Save to CSV
df.to_csv('csv//temp//temp.csv', index=False)



# ## Model/Series column clean up

# Read the CSV file into a Pandas DataFrame
df2 = pd.read_csv('csv//temp//temp.csv')
df = pd.read_csv('csv//awb_db_complete21.03.2024.csv', low_memory=False)

# Filter rows that contain 'LAPTOP' in the 'Product Type' column
product_type_filter = 'LAPTOP'
df = df[df['ProductType'].str.contains(product_type_filter, na=False)]

# Convert the 'Model' column to a string and lowercase it
df['Model'] = df['Model'].astype(str).str.lower()

# Create a set of unique entries in the 'Model' column to compare against
model_set = set(df['Model'])

# If 'model' entry string in df2 is only numeric, append 'series' entry to start of the string
df2['model'] = df2.apply(lambda row: str(row['series']) + ' ' + str(row['model']) if str(row['model']).isnumeric() else row['model'], axis=1)

# Find the most similar entry from the model_set and replace the original entry with the best match if the similarity score is above 75
df2['model'] = df2['model'].apply(lambda model: process.extractOne(str(model), model_set, scorer=fuzz.token_sort_ratio)[0] if process.extractOne(str(model), model_set, scorer=fuzz.token_sort_ratio)[1] > 75 else model)

# Drop rows where similarity score is below 75
df2 = df2[df2['model'].apply(lambda model: process.extractOne(str(model), model_set, scorer=fuzz.token_sort_ratio)[1] > 75)]

# Strip 'notebook', 'pc', 'laptop' and whitespace from the model entries
df2['model'] = df2['model'].str.replace('notebook', '').str.replace('pc', '').str.replace('laptop', '').str.strip()

# Drop rows where model entry string = 'nan' or 'cheap gaming laptop'
df2 = df2[~df2['model'].isin(['cheap gaming laptop', 'nan'])]

print(df2)



# Model entry cleanup
# if model contains the corresponding brand string from the same row, remove the brand string from the model entry
df2['model'] = df2.apply(lambda row: row['model'].replace(row['brand'], '').strip(), axis=1)

# Strip leading whitspace from model entries
df2['model'] = df2['model'].str.lstrip()



# # Save dataframe as csv file

# Drop duplicates
df2.drop_duplicates(inplace=True)

# Save df as a CSV file and display it
df2.to_csv(f'dataset//update//update_cleaned.csv', encoding='utf-8', index=False)

df = pd.read_csv(f'dataset//update//update_cleaned.csv')
print(df)

print('Data cleanup complete')



# # Update the base dataset
base = 'dataset//base//base.csv'

# Clone base and save as a new file
df = pd.read_csv(base)
df.to_csv(f'dataset//base//base_previous_version.csv', encoding='utf-8', index=False)

update_dataset(base, df)

# Update the Google Sheet
base = 'dataset//base//base.csv'
df = pd.read_csv(base)
gsheets_connect(df, 'C://Users//jack//Documents//aiken_upload_pipeline//Python_scripts//Google API Credentials//aiken-data-upload-1047684b4bce.json', 'Dataset', '1frCYK51QDUUeJXcCkd4y8Fy55ZW7w_kY-x3yvj7tIwY')


print('Base dataset updated')

