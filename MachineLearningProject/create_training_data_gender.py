# Script to create training data for gender

import shutil
import os
import csv
import sys

input_directory = sys.argv[1]
profile_file = input_directory + "/profile/profile.csv"
source_folder = input_directory+"/image/"
destination_folder =sys.argv[2]


male_folder_name ='male/'
female_folder_name='female/'

def create_labels():
    try:
        os.makedirs(destination_folder+male_folder_name)
        os.makedirs(destination_folder+female_folder_name)
    except OSError as e:
        print(e)

# Create a mapping of user and associated gender
def create_profile_user_gender_mapping():
    user_gender_dic ={}
    with open(profile_file, mode='r') as input_path:
        reader = csv.reader(input_path)
        next(reader)
        user_gender_dic ={row[1]:row[3] for row in reader}
    return user_gender_dic

# Place all images in the source folder into male/female
# folders based on the  user_gender_dic mapping.
def prepare_training_data_set(user_gender_dic):
    for user_id,_gender in user_gender_dic.items():
        gender = int(_gender)
        if gender == 1.0:
            shutil.copyfile(source_folder+user_id+".jpg", destination_folder+female_folder_name+user_id+".jpg")
        elif gender == 0.0:
            shutil.copyfile(source_folder+user_id+".jpg", destination_folder+male_folder_name+user_id+".jpg")
        else:
            #shutil.copyfile(source_folder+user_id+".jpg", destination_folder+other_folder_name)
            # raise Exception("Error")
            pass


create_labels()
user_gender_dic = create_profile_user_gender_mapping()
prepare_training_data_set(user_gender_dic)