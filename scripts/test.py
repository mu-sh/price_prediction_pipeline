import pandas as pd

ent = pd.read_csv('source_csv//enterprise_inventory.csv')
aiken = pd.read_csv('source_csv//products.csv')

print(ent.head())
print(aiken.head())

# Select only the columns we need
ent = ent[['ProductType', 'Manufacturer', 'Model']]


# Append one dataframe to another
merged = aiken._append(ent, ignore_index=True)

print(merged.head(200))

print(merged['ProductType'].unique())

# Lowercase all strings in the dataframe

merged = merged.apply(lambda x: x.str.lower() if x.dtype == "object" else x)

print(merged.head(200))

# Save to csv

merged.to_csv('source_csv//merged_inventory.csv', index=False)