from sklearn.model_selection import train_test_split
from sklearn.model_selection import RandomizedSearchCV
from sklearn.metrics import make_scorer
from sklearn.metrics import mean_absolute_error, explained_variance_score
from sklearn.metrics import mean_squared_error, r2_score
import json
from joblib import dump
import numpy as np
import os
import pandas as pd
from collections import Counter
from sklearn.datasets import make_classification
from imblearn.over_sampling import RandomOverSampler
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor
from datetime import date




# Define the hyperparameters to tune
param_dist = {
    'n_estimators': [10, 50, 100, 200, 500],
    'max_depth': [None, 10, 20, 30, 40, 50],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4],
    'max_features': ['sqrt', 'log2']
}



# Define custom scoring functions
def mse(y_true, y_pred):
    return mean_squared_error(y_true, y_pred)

def rmse(y_true, y_pred):
    return np.sqrt(mean_squared_error(y_true, y_pred))

def r2(y_true, y_pred):
    return r2_score(y_true, y_pred)

# Define the scoring metrics
scoring = {
    'MAE': make_scorer(mean_absolute_error, greater_is_better=False),
    'EVS': make_scorer(explained_variance_score),
    'MSE': make_scorer(mse),
    'RMSE': make_scorer(rmse),
    'R2': make_scorer(r2)
}


# define dataset
df = pd.read_csv('csv//02-11-23_clean_output8719row.csv')

# Remove 'nvidia' and 'amd' from the gpu column
df['gpu'] = df['gpu'].astype(str).str.lower().str.replace('nvidia', '', regex=True).str.replace('amd', '', regex=True).str.strip()
# Remove duplicate rows
df.drop_duplicates(inplace=True)

# Remove irrelevant columns
df.drop(['title', 'sold_date', 'link', 'seller notes', 'series', 'operating system', 'type', 'condition', 'processor', 'features', 'item number'], axis=1, inplace=True)

# Handle missing values
df.dropna(inplace=True)

# Split the dataset into training and testing sets
X = df.drop('price', axis=1)
y = df['price']

# Convert the 'price' variable to a binary variable
threshold = 50
y = np.where(y > threshold, 1, 0)

# summarize class distribution
print(Counter(y))
# define oversampling strategy
oversample = RandomOverSampler(sampling_strategy='minority')
# fit and apply the transform
X_over, y_over = oversample.fit_resample(X, y)

# summarize class distribution
print(Counter(y_over))

# Convert categorial variables with label encoder
categorical_cols = ['brand', 'processor i series', 'processor generation', 'storage type','gpu', 'model']
le_dict = {}

for col in categorical_cols:
    le = LabelEncoder()
    X[col] = le.fit_transform(X[col])
    le_dict[col] = le

# Create the directory if it doesn't exist
directory = f'models//{date.today()}'
if not os.path.exists(directory):
    os.makedirs(directory)

# Save the trained LabelEncoder objects
for col, le in le_dict.items():
    dump(le, f'{directory}//le_{col}.joblib')

# define oversampling strategy
oversample = RandomOverSampler(sampling_strategy='minority')

# fit and apply the transform
X_over, y_over = oversample.fit_resample(X, y)

# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X_over, y_over, test_size=0.2, random_state=1, stratify=y_over)

# Create a random forest regressor
reg = RandomForestRegressor(random_state=42)

# Initialize RandomizedSearchCV
random_search = RandomizedSearchCV(estimator=reg, param_distributions=param_dist, scoring=scoring, refit='MAE', n_iter=10, cv=5, verbose=2, random_state=42)

# Fit the random search model
random_search.fit(X_train, y_train)

# Get the results of the best model
best_results = random_search.cv_results_

# Make predictions on the testing set using the best estimator
y_pred = random_search.best_estimator_.predict(X_test)

# Create the directory if it doesn't exist
directory = f'models//{date.today()}'
if not os.path.exists(directory):
    os.makedirs(directory)

# Save the best performing model
dump(random_search.best_estimator_, f'{directory}//best_model_{date.today()}.joblib')

# Convert numpy arrays to lists
for key in best_results.keys():
    if isinstance(best_results[key], np.ndarray):
        best_results[key] = best_results[key].tolist()

# Log the performance of each model
log_file = 'logs//model_performance_log.json'
data = []

if os.path.exists(log_file):
    try:
        with open(log_file, 'r') as file:
            data = json.load(file)
    except json.JSONDecodeError:
        print("JSONDecodeError encountered. Initialized data as an empty list.")




# Modify the above to include the following:
'''
# Convert categorial variables with label encoder
categorical_cols = ['brand', 'processor i series', 'processor generation', 'storage type','gpu', 'model']
le_dict = {}

for col in categorical_cols:
    le = LabelEncoder()
    stock[col] = le.fit_transform(stock[col])
    le_dict[col] = le

# Save the trained LabelEncoder objects
for col, le in le_dict.items():
    dump(le, f'models//le_{col}.joblib')

'''
