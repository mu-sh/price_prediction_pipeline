import pandas as pd
import os


def update_dataset(file_path, new_data):
    # Load existing data
    df = pd.read_csv(file_path)

    # Concatenate existing data with new data
    updated_df = pd.concat([df, new_data], ignore_index=True)

    print(f"{len(updated_df)} rows after update")
    print(f"Number of unique item numbers after update: {len(updated_df['item number'].unique())}")

    # Print count of duplicate item numbers
    print(f"Number of duplicated entries after update: {updated_df.duplicated(subset='item number').sum()}")

    # Drop duplicates
    updated_df.drop_duplicates(subset='item number', inplace=True)

    print(f"{len(updated_df)} rows after dropping duplicates")

    # Save updated data
    updated_df.to_csv(file_path, index=False)





'''
# Iterate over all files in the 'csv//complete//' directory
for file in os.listdir('csv//complete//'):
    if file.endswith('.csv'):
        # Read csv and merge with existing data
        update = pd.read_csv('csv//complete//' + file)
        print(file)
        file_path = 'dataset//base//base2.csv'
        update_dataset(file_path, update)
'''


      