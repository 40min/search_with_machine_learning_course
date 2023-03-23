import os
import argparse
import re
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import csv

# Useful if you want to perform stemming.
import nltk
stemmer = nltk.stem.PorterStemmer()

categories_file_name = r'/workspace/datasets/product_data/categories/categories_0001_abcat0010000_to_pcmcat99300050000.xml'

queries_file_name = r'/workspace/datasets/train.csv'
output_file_name = r'/workspace/datasets/fasttext/labeled_queries.txt'

parser = argparse.ArgumentParser(description='Process arguments.')
general = parser.add_argument_group("general")
general.add_argument("--min_queries", default=1,  help="The minimum number of queries per category label (default is 1)")
general.add_argument("--output", default=output_file_name, help="the file to output to")

args = parser.parse_args()
output_file_name = args.output

min_queries = int(args.min_queries) if args.min_queries else 1

# The root category, named Best Buy with id cat00000, doesn't have a parent.
root_category_id = 'cat00000'

tree = ET.parse(categories_file_name)
root = tree.getroot()

# Parse the category XML file to map each category id to its parent category id in a dataframe.
categories = []
parents = []
for child in root:
    id = child.find('id').text
    cat_path = child.find('path')
    cat_path_ids = [cat.find('id').text for cat in cat_path]
    leaf_id = cat_path_ids[-1]
    if leaf_id != root_category_id:
        categories.append(leaf_id)
        parents.append(cat_path_ids[-2])
parents_df = pd.DataFrame(list(zip(categories, parents)), columns =['category', 'parent'])

# Read the training data into pandas, only keeping queries with non-root categories in our category tree.
queries_df = pd.read_csv(queries_file_name)[['category', 'query']]
queries_df = queries_df[queries_df['category'].isin(categories)]

# IMPLEMENT ME: Convert queries to lowercase, and optionally implement other normalization, like stemming.
all_except_alphanum = re.compile(r"[^\d\w]+")


def query_comb(query: str) -> str:
    q_lower = query.lower()
    q_cleaned = re.sub(all_except_alphanum, " ", q_lower)
    q_stemmed_list = [stemmer.stem(w) for w in q_cleaned.split()]
    if not q_stemmed_list:
        return ""
    q_trimmed = " ".join(q_stemmed_list)
    return q_trimmed


queries_df['query'] = queries_df['query'].map(query_comb)
queries_df = queries_df.drop(queries_df[queries_df['query'] == ""].index)

# IMPLEMENT ME: Roll up categories to ancestors to satisfy the minimum number of queries per category.
category_counts = queries_df.groupby(['category'])['query'].size().reset_index(name="counts")
threshold = 1
num_of_iterations = 0
while threshold <= min_queries:
    while category_counts.counts.lt(threshold).any():
        num_of_iterations += 1
        queries_df = pd.merge(queries_df, category_counts, on="category", how="left")
        queries_df = pd.merge(queries_df, parents_df, on="category", how="left")
        condition = queries_df["counts"] < threshold
        queries_df.loc[condition, "category"] = queries_df.loc[condition, "parent"]
        category_counts = queries_df.groupby(['category'])['query'].size().reset_index(name="counts")
        queries_df = queries_df.drop(columns=["counts", "parent"], axis=1)

    threshold += 1

queries_df.fillna({"category": root_category_id}, inplace=True)
print(f"Number of iterations: {num_of_iterations}")

a = queries_df[queries_df['query'] == ""]
b = queries_df[queries_df['category'] == ""]

# Create labels in fastText format.
queries_df['label'] = '__label__' + queries_df['category']

# Output labeled query data as a space-separated file, making sure that every category is in the taxonomy.
queries_df = queries_df[queries_df['category'].isin(categories)]
queries_df['output'] = queries_df['label'] + ' ' + queries_df['query']
queries_df[['output']].to_csv(output_file_name, header=False, sep='|', escapechar='\\', quoting=csv.QUOTE_NONE, index=False)
