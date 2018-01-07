import random
import sys
import csv
import os
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from collections import Counter

#Command line args and setting up paths
input_directory = sys.argv[1]
output_directory = sys.argv[2]
profile_test = input_directory + "profile/profile.csv"
relation_test = input_directory + "relation/relation.csv"
train_text_dir = "/data/training/text/"
test_text_dir = input_directory + "text/"
image_test = input_directory+"/image"
liwc_test = input_directory + "LIWC/LIWC.csv"
tf_path = "/home/itadmin/tf_image_classification"

#Loading Data frames
df_trained_upu = pd.read_csv("/home/itadmin/user_page_user/trained.csv",index_col=0)
df_profile_test = pd.read_csv(profile_test,index_col=0)
df_relation_test = pd.read_csv(relation_test,index_col=0)
df_relation_test.like_id = df_relation_test.like_id.astype(str)
df_trained_upu.like_id = df_trained_upu.like_id.astype(str)
df_profile_train = pd.read_csv('/data/training/profile/profile.csv',index_col=0)
df_relation_train = pd.read_csv("/data/training/relation/relation.csv",index_col=0)
df_relation_train.like_id = df_relation_train.like_id.astype(str)
df_liwc_train = pd.read_csv('/data/training/LIWC/LIWC.csv')
merge_df_train_liwc = (pd.merge(df_profile_train, df_liwc_train, left_on='userid', right_on='userId'))
df_liwc_test = pd.read_csv(liwc_test)
merge_df_test_liwc = (pd.merge(df_profile_test, df_liwc_test, left_on='userid', right_on='userId'))


# Add agegroup column to profile dataframe
df_profile_train['agegroup'] = 0
df_profile_train['agegroup'].loc[df_profile_train['age']<25]=0
df_profile_train['agegroup'].loc[(df_profile_train['age']>=25) & (df_profile_train['age']<35)]=1
df_profile_train['agegroup'].loc[(df_profile_train['age']>=35) & (df_profile_train['age']<50)]=2
df_profile_train['agegroup'].loc[df_profile_train['age']>=50]=3

counts = df_relation_train['like_id'].value_counts()
new_df = df_relation_train[df_relation_train['like_id'].isin(counts[counts < 900].index & counts[counts > 1].index)]

# training data frame to apply NB and LR on likes
df_relation_grouped = new_df.groupby('userid',as_index=False).agg({'like_id': lambda x: "%s" % ' '.join(x)})
merge_df_train_relation = (pd.merge(df_profile_train, df_relation_grouped, left_on='userid', right_on='userid'))
df_relation_grouped2 = df_relation_test.groupby('userid',as_index=False).agg({'like_id': lambda x: "%s" % ' '.join(x)})
merge_df_test_relation = (pd.merge(df_profile_test, df_relation_grouped2, left_on='userid', right_on='userid'))

# LR on gender and age from text................................................................
# Preparing the training and test data
df_profile_train["text"] = ""
ind = 0

for row in df_profile_train['userid']:
    text_file = row + ".txt"
    text_file = open(train_text_dir + text_file, 'rt',encoding="ISO-8859-1")
    text = text_file.read()
    df_profile_train.set_value(ind, "text", text)
    ind+=1
    text_file.close()

df_profile_test["text"] = ""
ind = 0

for row in df_profile_test['userid']:
    text_file = row + ".txt"
    text_file = open(test_text_dir + text_file, 'rt',encoding="ISO-8859-1")
    text = text_file.read()
    df_profile_test.set_value(ind, "text", text)
    ind+=1
    text_file.close()

# Add agegroup column to profile dataframe
df_profile_train['agegroup'] = 0
df_profile_train['agegroup'].loc[df_profile_train['age']<25]=0
df_profile_train['agegroup'].loc[(df_profile_train['age']>=25) & (df_profile_train['age']<35)]=1
df_profile_train['agegroup'].loc[(df_profile_train['age']>=35) & (df_profile_train['age']<50)]=2
df_profile_train['agegroup'].loc[df_profile_train['age']>=50]=3

gender_train = df_profile_train.loc[:,['text', 'gender']]
gender_test = df_profile_test.loc[:,['text', 'gender']]
age_train = df_profile_train.loc[:,['text', 'agegroup']]
age_test = df_profile_test.loc[:,['text', 'agegroup']]

# Training Naive Bayes model
count_vect = CountVectorizer()
X_gender_train = count_vect.fit_transform(gender_train['text'])
y_gender_train = gender_train['gender']
X_age_train = count_vect.fit_transform(age_train['text'])
y_age_train = age_train['agegroup']
clf_gender = LogisticRegression()
clf_gender.fit(X_gender_train, y_gender_train)
clf_age = LogisticRegression()
clf_age.fit(X_age_train, y_age_train)

# Predict test data
X_gender_test = count_vect.transform(gender_test['text'])
y_gender_LR_text = clf_gender.predict(X_gender_test)
X_age_test = count_vect.transform(age_test['text'])
y_age_LR_text = clf_age.predict(X_age_test)
#....................................................................................................

# User-Page-User Approach on gender, age and personalities............................................
# Inner join of the data frames
df = pd.merge(df_relation_test,df_trained_upu)

# Computing user by user from trained data
func = {'gender': lambda x:x.value_counts().index[0], 'agegroup': lambda x:x.value_counts().index[0], 'ope': ['mean'], 'con': ['mean'], 'ext': ['mean'], 'agr': ['mean'], 'neu': ['mean']}
test_df = df.groupby('userid',as_index=False).agg(func)
test_df.columns = test_df.columns.get_level_values(0)

#setting the order of users to match profile.csv
test_df = test_df.set_index('userid')
test_df = test_df.reindex(index=df_profile_test['userid'])
test_df = test_df.reset_index()

#for accuracy and RMSE computation
y_gender_upu = test_df['gender']
y_age_upu = test_df['agegroup']
ocean = ['ope','con','ext','agr','neu']
y_pers_upu = test_df[ocean]
y_gender_upu[np.isnan(y_gender_upu)]=1.0
y_age_upu[np.isnan(y_age_upu)]=0
y_pers_upu.ope.fillna(3.91, inplace=True)
y_pers_upu.ext.fillna(3.49, inplace=True)
y_pers_upu.con.fillna(3.45, inplace=True)
y_pers_upu.agr.fillna(3.58, inplace=True)
y_pers_upu.neu.fillna(2.73, inplace=True)
#.....................................................................................................

# NB on age and gender based on relations.............................................................................

y_likes_gender_train = merge_df_train_relation['gender']
y_likes_age_train = merge_df_train_relation['agegroup']

count_vect2 = CountVectorizer()
X_train_age = count_vect2.fit_transform(merge_df_train_relation['like_id'])
X_test_age = count_vect2.transform(merge_df_test_relation['like_id'])
X_train_gender = count_vect2.fit_transform(merge_df_train_relation['like_id'])
X_test_gender = count_vect2.transform(merge_df_test_relation['like_id'])

clf_likes = MultinomialNB()
clf_likes.fit(X_train_gender, y_likes_age_train)
clf2_likes = MultinomialNB()
clf2_likes.fit(X_train_gender, y_likes_gender_train)
y_age_NB_likes = clf_likes.predict(X_test_age)
y_gender_NB_likes = clf2_likes.predict(X_test_gender)

#..........................................................................................................

# LR on age and gender based on likes........................................................................

y_gender_likes = merge_df_train_relation['gender']

count_vect3 = CountVectorizer()
X_train_likes = count_vect3.fit_transform(merge_df_train_relation['like_id'])
X_test_likes = count_vect3.transform(merge_df_test_relation['like_id'])

clf_LR = LogisticRegression()
clf_LR.fit(X_train_likes, y_gender_likes)
y_gender_LR_likes = clf_LR.predict(X_test_likes)

y_age_likes = merge_df_train_relation['agegroup']

clf2_LR = LogisticRegression()
clf2_LR.fit(X_train_likes, y_age_likes)
y_age_LR_likes = clf2_LR.predict(X_test_likes)
#...............................................................................................................

#Linear regression on LIWC................................................................................

# Preparing the train and test data - for Linear Regression to predict personalities
big5 = ['ope','ext','con','agr','neu']
LIWC_features = [x for x in df_liwc_train.columns.tolist()[:]]
LIWC_features.remove('userId')
X_train_liwc = merge_df_train_liwc[LIWC_features]
y_train_liwc = merge_df_train_liwc[big5]
X_test_liwc = merge_df_test_liwc[LIWC_features]

# Training and evaluating a linear regression model
linreg = LinearRegression()
linreg.fit(X_train_liwc,y_train_liwc)

# Predicting the personalities
y_predicted_ocean = linreg.predict(X_test_liwc)

#................................................................................................................

# Gender prediction on images.............................................................................

# Initialize the tensor flow graph object from retrained_graph.pb after retraining the inception V3 model.
def initialize_graphdef():
     with tf.gfile.FastGFile("/home/itadmin/tf_image_classification/tf_files/retrained_graph.pb", 'rb') as f:

        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())
        _tensor_object = tf.import_graph_def(graph_def, name='')

# Run Image classification on test input image
# Returns the most like category as the predicted result
def classify_image(image_path):
    image_data = tf.gfile.FastGFile(image_path, 'rb').read()
    label_lines = [line.rstrip() for line
                   in tf.gfile.GFile("/home/itadmin/tf_image_classification/tf_files/retrained_labels.txt")]

    with tf.Session() as sess:
        softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')

        predictions = sess.run(softmax_tensor, \
                    {'DecodeJpeg/contents:0': image_data})

        # Order by label that has highest probability.
        top_k = predictions[0].argsort()[-len(predictions[0]):][::-1]

        if top_k[0]==1:
            return 0.0
        else:
            return 1.0

# Maintain a dictionary of user and the corresponding gender
# predicted by Inception V3 model
def get_user_gender_mapping():
    user_gender_mapping ={}
    directory = image_test
    file_list = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.jpg')]
    for g in file_list:
        user_file = os.path.basename(g)
        user = os.path.splitext(user_file)[0]
        gender = classify_image(g)
        user_gender_mapping[user]= gender

    return user_gender_mapping


initialize_graphdef()
user_gender_mapping = get_user_gender_mapping()

#........................................................................................................................................

gender_values = []
age_values = []

for a, b, c in zip(y_age_LR_likes, y_age_NB_likes, y_age_LR_text):
    temp = [a,b,c]
    count = Counter(temp)
    i = count.most_common()[0][0]
    if i==0.0:
        age_values.append("xx-24")
    elif i==1:
        age_values.append("25-34")
    elif i==2:
        age_values.append("35-49")
    else:
        age_values.append("50-xx")

for a, b, e in zip(y_gender_LR_text, y_gender_LR_likes, df_profile_test['userid']):
    val=user_gender_mapping[e]
    temp = [a, b, val]
    count = Counter(temp)
    i = count.most_common()[0][0]
    if i==1.0:
        gender_values.append("female")
    else:
        gender_values.append("male")

#Parsing through the test data
with open(profile_test) as csvfile:
        testreader = csv.reader(csvfile,delimiter=',')
        header = next(testreader)
        index = 0
        for row in testreader:
             f=output_directory+row[1]+".xml"
             testfile=open(f,"w")
             testfile.write("<user\n")
             testfile.write("id=\"%s\"\n"%row[1])
             testfile.write("age_group=\"%s\"\n"%age_values[index])
             testfile.write("gender=\"%s\"\n"%gender_values[index])
             testfile.write("extrovert=\"%.2f\"\n"%y_pers_upu['ext'][index])
             testfile.write("neurotic=\"%.2f\"\n"%y_predicted_ocean[index][4])
             testfile.write("agreeable=\"%.2f\"\n"%y_predicted_ocean[index][3])
             testfile.write("conscientious=\"%.2f\"\n"%y_pers_upu['con'][index])
             testfile.write("open=\"%.2f\"\n"%y_pers_upu['ope'][index])
             testfile.write("/>")
             index+=1

csvfile.close();
