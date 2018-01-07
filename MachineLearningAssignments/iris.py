#################################################################
#
#  TCSS555 - HW 1
#
#  Martine De Cock
#
#################################################################

import pandas as pd
import numpy as np
from sklearn.model_selection import KFold, cross_val_score, StratifiedKFold
from sklearn import tree
from sklearn import metrics

# Read the dataset into a dataframe and map the labels to numbers
df = pd.read_csv('iris.csv')
map_to_int = {'setosa':0, 'versicolor':1, 'virginica':2}
df["label"] = df["species"].replace(map_to_int)
print(df)

# Separate the input features from the label
features = list(df.columns[:4])
X = df[features]
y = df["label"]






# Train a decision tree and compute its training accuracy
clf = tree.DecisionTreeClassifier(max_depth=2, criterion='entropy')
clf.fit(X, y)
print(metrics.accuracy_score(y,clf.predict(X)))

# kf = KFold(n_splits=10)
# print(kf)
# for train_index, test_index in kf.split(X):
#     # print(train_index, test_index)
#     X_train, X_test = X[train_index],X[test_index]
#     y_train, y_test = y[train_index],y[test_index]

cross_val_scores =cross_val_score(clf,X, y, cv=10, scoring='accuracy') 
print(cross_val_scores)
print("Accuracy is %0.2f (+/- %0.2f)" %(cross_val_scores.mean(),\
     cross_val_scores.std()*2))


# cross_val_scores =cross_val_score(clf,X, y, cv=StratifiedKFold(n_splits=10,shuffle=True)) 
# print(cross_val_scores)
# print("Accuracy is %0.2f (+/- %0.2f)", cross_val_scores.mean(), cross_val_scores.std()*2)

