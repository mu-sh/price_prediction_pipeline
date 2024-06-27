import pandas as pd
from datasetupdater import update_dataset

file = 'dataset//base//base.csv'
update = 'dataset//base//update_cleaned.csv'

# Assuming df1, df, df3 are your dataframes
df = pd.read_csv(file)

# print unique model entries
print(df['model'].unique())

# print unique screen size entries
print(df['screen size'].unique())


print(len(df))



df['screen size'] = df['screen size'].apply(lambda x: round(float(''.join(c for c in str(x) if c.isdigit() or c == '.')), 1) if ''.join(c for c in str(x) if c.isdigit() or c == '.') and '.' in str(x) and str(x)[-1] != '.' else ''.join(c for c in str(x) if c.isdigit()))

# Drop rows with missing screen size
df = df.dropna(subset=['screen size'])

df = df[df['screen size'] != '']

# Convert screen size to float
df['screen size'] = df['screen size'].astype(float)

# Drop entries with screen size less than 10
df = df[df['screen size'] >= 10]



# Model entry cleanup
# if model contains the corresponding brand string from the same row, remove the brand string from the model entry
df['model'] = df.apply(lambda row: row['model'].replace(row['brand'], '').strip() if isinstance(row['model'], str) else row['model'], axis=1)

# Strip leading whitspace from model entries
df['model'] = df['model'].str.lstrip()

# print unique model entries
#print(df['model'].unique())

# print unique screen size entries
#print(df['screen size'].unique())

#df.to_csv(file, index=False)