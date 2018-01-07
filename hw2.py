# course: TCSS555
# Homework 2
# date: 10/03/2017
# name: Martine De Cock
# description: Training and testing decision trees with discrete-values attributes

import copy
import csv
import math
import sys

import pandas as pd


class DecisionNode:
    
    # A DecisionNode contains an attribute and a dictionary of children. 
    # The attribute is either the attribute being split on, or the predicted label if the node has no children.
    def __init__(self, attribute):
        self.attribute = attribute
        self.children = {}

    # Visualizes the tree
    def display(self, level = 0):
        if self.children == {}: # reached leaf level
            print(": ", self.attribute, end="")
        else:
            for value in self.children.keys():
                prefix = "\n" + " " * level * 4
                print(prefix, self.attribute, "=", value, end="")
                self.children[value].display(level + 1)
     
    # Predicts the target label for instance x
    def predicts(self, x):
        if self.children == {}: # reached leaf level
            return self.attribute
        value = x[self.attribute]
        subtree = self.children[value]
        return subtree.predicts(x)


# Entropy Calculation
def calculate_entropy(positive_examples, negative_examples):
    a = positive_examples / (positive_examples + negative_examples)
    b = negative_examples / (positive_examples + negative_examples)

    val = 0
    if a > 0:
        val = val - (a * math.log(a, 2))
    if b > 0:       
        val = val - (b * math.log(b, 2))
    return val

# Get {Attribute_Name: Gain} mapping for all attributes in the attribute_list
# total_entropy is the entropy at this level calculated using positive and negative
# examples irrespective of attribute type
def get_attribute_gain_mapping(df, total_entropy, total_examples, attribute_list, label_attribute, label_options):
   
    positive_label = label_options[1]
    negative_label = label_options[0]

    attribute_gain_dictionary = {}

    for attribute in attribute_list:
        child_dic = {}

        # Record the attribute_type: (entropy, total_examples for the type)
        # for each attribute type for a given attribute.
        # Eg. For attribute outllok, attribute types are [sunny, rainy, overcast]
        # Record entropy and count of such types for sunny, rainy,overcast. 
        attribute_types = df[attribute].unique()
        for at in attribute_types:
            positive_flag = (df[attribute] == at) & (df[label_attribute] == positive_label)
            negative_flag = (df[attribute] == at) & (df[label_attribute] == negative_label)

            positive_count = len(df[positive_flag])
            negative_count = len(df[negative_flag])

            type_entropy = calculate_entropy(positive_count, negative_count)

            child_dic.update(
                {
                    at: (type_entropy, positive_count + negative_count)
                }
            )

        # Calculate the attribute entropy coming from
        # all attribute types and sum them up.
        attribute_entropy = 0

        for k, v in child_dic.items():
            (type_entropy, type_count) = child_dic[k]
            attribute_entropy = attribute_entropy + \
                ((type_count / total_examples) * type_entropy)

         # Calculate Gain for an entropy
         # Gain = total_entropy - attribute_entropy
        gain_attribute = total_entropy - attribute_entropy
        attribute_gain_dictionary.update(
            {
                attribute: gain_attribute
            }
        )

    return attribute_gain_dictionary

# Get all possible counts for given set of training examples
# These include 1. the count of positive examples
# 2. count of negative examples
# 3. count of all examples.
# label_options is a list of various target attributes
# eg [no,yes], [0,1]
def get_example_types_count(df,label_options, label_attribute):
    # We consider label_options[0] to refer to
    # negative examples and label_options[1] to
    # refer to positive examples.
    postive_label = label_options[1]
    negative_label = label_options[0]
    
    # filter to be used in filtering the training examples
    # stored in pandas data frame as positive and negative.
    plus_flag = (df[label_attribute] == postive_label)
    minus_flag = (df[label_attribute] == negative_label)
   
    total_positive_examples = len(df[plus_flag])
    total_negative_examples = len(df[minus_flag])
    total_examples = total_positive_examples+ total_negative_examples

    return [total_positive_examples, total_negative_examples, total_examples]


# Function to return that target level attribute
# which repeats the most in the given data frame.
def get_majority_element(df, label_options, target):
    maj_option = df[target].value_counts().idxmax()
    return maj_option

# Recursively build the decision tree level by level
# by chosing the attribute that has the highest gain at
# each level. Once the attribute is selected, we explore
# all its possible values as child branches recursively
def buildId3(df, attribute_list, label_attribute, label_options, maj_option):
    if not attribute_list:
        return DecisionNode(maj_option)

    [pos,neg,total] = get_example_types_count(df, label_options, label_attribute)
    
    if total==0:
        return DecisionNode(maj_option)
    if pos==0 and neg>0:
        return DecisionNode(label_options[0])
    elif neg==0 and pos>0:
        return DecisionNode(label_options[1])
  
    # Calculate entropy at this level
    entropy = calculate_entropy(pos,neg)
    
    # Get the dictionary containing the {attribute_name: gain} mapping for all the attributes
    # in the attribute_list
    dic = get_attribute_gain_mapping(df, entropy, total, attribute_list, label_attribute, label_options)

    # Get the attribute which has the maximum gain
    attribute = max(dic, key=dic.get)

    # Construct the DecisionNode at this level for the above attribute
    root = DecisionNode(attribute)

    # Explore all branches for the selected attribute
    for path in df[attribute].unique():
        # Filter the data frame to include
        # attribute=path condition
        # eg: if Outlook has [sunny, overcast]
        # then this filter would be something like
        # [outlook=sunny]
        filtered_df_flag = (df[attribute] == path)
        filtered_df = df[filtered_df_flag]

        # Make a copy of this attribute list
        # since we have to come back to this level
        # to explore other paths with all attributes at this level.
        attribute_list_copy = copy.deepcopy(attribute_list)
        attribute_list_copy.remove(attribute)
      
        # Find which category of examples occur the most for this dataframe
        maj_option = get_majority_element(filtered_df, label_options, label_attribute)

        # Recurse on child
        child_node = buildId3(filtered_df, attribute_list_copy, label_attribute, label_options, maj_option)
        
        # Update the children dictionary for the root node
        root.children.update(
            {
                path: child_node
            })
    return root


####################   MAIN PROGRAM ######################

# Read User Inputs
train = pd.read_csv(sys.argv[1], quoting = csv.QUOTE_ALL) # training data

test = pd.read_csv(sys.argv[2], quoting = csv.QUOTE_ALL)  # test data


target = sys.argv[3]  # target attributes

attribute_list = train.columns.tolist()

# create Pandas dataframe for training data
df2 = train[attribute_list]

# list of possible target attribute values (eg: yes/no, 0/1)
label_options = df2[target].unique().tolist()

# target attribute that repeats the most number of times in the training examples. 
maj_option = get_majority_element(df2, label_options, target)

# Remove the target attribute from attribute list used for building decision tree
attribute_list.remove(target)

# Build decision tree
tree = buildId3(df2, attribute_list, target, label_options, maj_option)

# Display the tree
tree.display()


# Evaluating the tree on the test data
correct = 0
for i in range(0, len(test)):
    if str(tree.predicts(test.loc[i])) == str(test.loc[i, target]):
        correct += 1
print("\nThe accuracy is: ", correct / len(test))
