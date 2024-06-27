

def merge_databases(aiken_path, blancco_path, output_path):
    aiken = pd.read_csv(aiken_path)
    blancco = pd.read_csv(blancco_path)

    # Save column lists as csv files (optional, adjust paths as needed)
    aiken_cols = pd.DataFrame(aiken.columns)
    aiken_cols.to_csv(output_path.replace('stock_database.csv', 'aiken_cols.csv'), index=False, header=False)

    blancco_cols = pd.DataFrame(blancco.columns)
    blancco_cols.to_csv(output_path.replace('stock_database.csv', 'blancco_cols.csv'), index=False, header=False)

    blancco['CollectionID'] = blancco['Business name'].str.split('-').str[1]
    blancco = blancco.drop(['Business name', 'BARCODE_y', 'Barcode_y'], axis=1)
    blancco['Barcode'] = blancco['BARCODE_x'].combine_first(blancco['Barcode_x'])
    blancco = blancco.drop(['BARCODE_x', 'Barcode_x'], axis=1)

    # Process Disk interface type, model, serial, and vendor
    for column, new_columns in [('Disk interface type', ['Disk1 type', 'Disk2 type', 'Disk3 type', 'Disk4 type']),
                                ('Disk model', ['Disk1 model', 'Disk2 model', 'Disk3 model', 'Disk4 model']),
                                ('Disk serial', ['Disk1 serial', 'Disk2 serial', 'Disk3 serial', 'Disk4 serial']),
                                ('Disk vendor', ['Disk1 vendor', 'Disk2 vendor', 'Disk3 vendor', 'Disk4 vendor']),
                                ('Disk capacity', ['Disk1 capacity', 'Disk2 capacity', 'Disk3 capacity', 'Disk4 capacity'])]:
        df_split = blancco[column].str.split('/', expand=True)
        df_split = df_split.iloc[:, :4]
        df_split.columns = new_columns
        blancco = blancco.join(df_split)

    # Header mapping
    header_mapping = {
        # Add your header mappings here as in the original code
    }
    blancco = blancco.rename(columns=header_mapping)

    # Drop unnecessary columns
    cols_to_drop = ['Maximum CPU frequency', 'Video card vendor', 'Report verification', 'Erasure target model', 'Disk index', 'Disk ID', 'Disk capacity', 'Disk model', 'Disk serial', 'Disk vendor', 'Disk interface type']
    blancco = blancco.drop(cols_to_drop, axis=1)

    # Add 'source' column to each DataFrame
    aiken['source'] = 'aiken'
    blancco['source'] = 'blancco'

    # Concatenate the two DataFrames
    df = pd.concat([aiken, blancco], ignore_index=True)

    # Sort and reset index
    df = df.sort_values(by='Audited').reset_index(drop=True)

    # Lowercase all column headers and values
    df.columns = map(str.lower, df.columns)
    df = df.apply(lambda x: x.astype(str).str.lower())

    # Filter df by collectionID for string beginning with 'j'
    df = df[df['collectionid'].str.startswith('j')]

    # Ensure that unitid and lotid are integers
    df['unitid'] = df['unitid'].astype(int)
    df['lotid_x'] = df['lotid_x'].astype(float).astype(int)

    # Save the DataFrame to a CSV file
    df.to_csv(output_path, index=False)