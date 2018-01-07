# course: TCSS555
# ML in Python
# date: 10/07/2017

# name: Martine De Cock
# description: Linear Regression for predicting sales based on advertising
# You are given the amount of thousands of dollars spent on advertising a product on TV, Radio, and in the Newspaper
# You need to predict the sales of the product (in terms of thousands of items)

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn import metrics

# Loading the data
data = pd.read_csv("http://www-bcf.usc.edu/~gareth/ISL/Advertising.csv", index_col=0)
print("\nFirst rows of the data")
print(data.head())
print("\nSummary statistics of the data")
print(data.describe())

# Subsetting a dataset
print("\nInspecting various subsets of the data")
sub_data = data.drop('TV',axis=1)
print(sub_data.head())
sub_data2 = data[(data.TV > 100) & (data.radio > 20)]
print(sub_data2.head())
sub_data3 = data[data.radio == 24]
print(sub_data3.head())

# Preparing the train and test data
feature_cols = ['TV', 'radio', 'newspaper']
X = data[feature_cols]
y = data.sales
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Fitting the model
linreg = LinearRegression()
linreg.fit(X_train, y_train)
print("\nCoefficients:", list(zip(feature_cols, linreg.coef_)))
print("Intercept:", linreg.intercept_)

# Evaluating the model
y_pred = linreg.predict(X_test)
print("\nMAE:", metrics.mean_absolute_error(y_test, y_pred))
print("MSE:", metrics.mean_squared_error(y_test, y_pred))
print("RMSE:", np.sqrt(metrics.mean_squared_error(y_test, y_pred)))
