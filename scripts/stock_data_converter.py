import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from joblib import load
from datetime import date

stock = pd.read_csv('csv//awb_db_complete07.12.2023.csv')
ebay = pd.read_csv('csv//02-11-23_clean_output8719row.csv')
ebay['gpu'] = ebay['gpu'].astype(str).str.lower().str.replace('nvidia', '', regex=True).str.replace('amd', '', regex=True)

# Filter stock data by ProducType = Laptop
stock = stock[stock['ProductType'] == 'LAPTOP']

# Create a dictionary of column names to rename
ebay_rename = {
    'price': 0,
    'brand': stock['Manufacturer'].astype(str).str.lower().str.strip(),
    'processor i series': stock['ProcGen'].astype(str).str.split().str[0].str.strip(), 
    'processor generation': stock['ProcGen'].astype(str).str.split().str[1].str[0].str.strip(), 
    'processor speed': stock['Processor'].astype(str).str.split().str[2].str.strip(), 
    'ram size': stock['TotalRAM'].astype(str).str.split().str[0].str.strip(), 
    'storage capacity': stock['Storage1Size'].astype(str).str.split().str[0].str.strip(), 
    'storage type': stock['Storage1Type'].astype(str).str.lower().replace({'sata ssd': 'ssd', 'nvme ssd': 'nvme', 'sata hdd': 'hdd'}).str.strip(),
    'screen size': stock['DisplaySize'].astype(str).str.replace('"', '').str.strip(), 
    'gpu': 'integrated',
    'model': stock['Model'].astype(str).str.lower().str.strip()
}

# Create a new dataframe using th dictionary to read in values from stock
stock = pd.DataFrame(ebay_rename)

print(stock.head(500))

# Filter the stock data processor i series column to only include i3, i5, i7, i9
stock = stock[stock['processor i series'].isin(['i3', 'i5', 'i7', 'i9'])]

# Filter stock manufacturer column to only include Dell, HP, Lenovo
stock = stock[stock['brand'].isin(['dell', 'hp', 'lenovo'])]

# Drop rows that contain 1 or 2 in the processeor generation column
stock = stock[~stock['processor generation'].isin(['1', '2'])]

# Drop rows that contain 'invalid' in the model column
stock = stock[stock['model'] != 'invalid']

# Drop rows which have 'nan' entries in the storage type column
stock = stock[stock['storage type'] != 'nan']

# print unique processor generations
print(stock['gpu'].unique())
print(ebay['gpu'].astype(str).str.lower().replace({'nvidia': '', 'amd': ''}).unique())

# read label encoders for gpu
le_gpu = load(f'models//{date.today()}//le_gpu.joblib')
print(le_gpu.classes_)

# Load the label encoders used during training
le_brand = load(f'models//{date.today()}//le_brand.joblib')
le_processor_i_series = load(f'models//{date.today()}//le_processor i series.joblib')
le_processor_generation = load(f'models//{date.today()}//le_processor generation.joblib')
le_storage_type = load(f'models//{date.today()}//le_storage type.joblib')
le_gpu = load(f'models//{date.today()}//le_gpu.joblib')
le_model = load(f'models//{date.today()}//le_model.joblib')

# Apply the label encoders to the new data
stock['brand'] = le_brand.transform(stock['brand'])
stock['processor i series'] = le_processor_i_series.transform(stock['processor i series'])
stock['processor generation'] = le_processor_generation.transform(stock['processor generation'])
stock['storage type'] = le_storage_type.transform(stock['storage type'])
stock['gpu'] = le_gpu.transform(stock['gpu'])
stock['model'] = le_model.transform(stock['model'])

# Load the trained model
model = load(f'models//{date.today()}//best_model_2023-12-07.joblib')

# Split the dataset into training and testing sets
features = stock.drop('price', axis=1)

# Use the model to make predictions
stock['predicted_price'] = model.predict(features)

print(stock.head(500))




