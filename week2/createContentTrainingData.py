import argparse
import multiprocessing
import glob
from collections import defaultdict
from time import sleep

from tqdm import tqdm
import os
import xml.etree.ElementTree as ET
from pathlib import Path

def transform_name(product_name):
    # IMPLEMENT
    return product_name

# Directory for product data
directory = r'./workspace/datasets/product_data/products/'

parser = argparse.ArgumentParser(description='Process some integers.')
general = parser.add_argument_group("general")
general.add_argument("--input", default=directory,  help="The directory containing product data")
general.add_argument("--output", default="./workspace/datasets/fasttext/output.fasttext", help="the file to output to")
general.add_argument("--label", default="id", help="id is default and needed for downsteam use, but name is helpful for debugging")

# IMPLEMENT: Setting min_products removes infrequent categories and makes the classifier's task easier.
general.add_argument("--min_products", default=0, type=int, help="The minimum number of products per category (default is 0).")

args = parser.parse_args()
output_file = args.output
path = Path(output_file)
output_dir = path.parent
if os.path.isdir(output_dir) == False:
        os.mkdir(output_dir)

if args.input:
    directory = args.input
# IMPLEMENT: Track the number of items in each category and only output if above the min
min_products = int(args.min_products)
names_as_labels = False
if args.label == 'name':
    names_as_labels = True

def _label_filename(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    labels = []
    for child in root:
        # Check to make sure category name is valid and not in music or movies
        if (child.find('name') is not None and child.find('name').text is not None and
            child.find('categoryPath') is not None and len(child.find('categoryPath')) > 0 and
            child.find('categoryPath')[len(child.find('categoryPath')) - 1][0].text is not None and
            child.find('categoryPath')[0][0].text == 'cat00000' and
            child.find('categoryPath')[1][0].text != 'abcat0600000'):
              # Choose last element in categoryPath as the leaf categoryId or name
              if names_as_labels:
                  cat = child.find('categoryPath')[len(child.find('categoryPath')) - 1][1].text.replace(' ', '_')
              else:
                  cat = child.find('categoryPath')[len(child.find('categoryPath')) - 1][0].text
              # Replace newline chars with spaces so fastText doesn't complain
              name = child.find('name').text.replace('\n', ' ')
              labels.append((cat, transform_name(name)))
    return labels

if __name__ == '__main__':
    files = glob.glob(f'{directory}/*.xml')
    cat_products = defaultdict(lambda: set())
    with multiprocessing.Pool() as p:
        print("Loading products")

        total_label_list = []
        read_bar = tqdm(total=len(files))
        for label_list in p.imap(_label_filename, files):
            for (cat, name) in label_list:
                cat_products[cat].add(name)
                total_label_list.append((cat, name))
            read_bar.update()
        read_bar.clear()
        read_bar.close()

    # shuf ./workspace/datasets/fasttext/pruned_labeled_products.txt --random-source=<(seq 99999) > ./workspace/datasets/fasttext/shuffled_pruned_labeled_products.txt
    # cat ./workspace/datasets/fasttext/shuffled_pruned_labeled_products.txt | sed -e "s/\([.\!?,'/()]\)/ \1 /g" | tr "[:upper:]" "[:lower:]" | sed "s/[^[:alnum:]_]/ /g" | tr -s ' ' > ./workspace/datasets/fasttext/normalized_shuffled_pruned_labeled_products.txt
    # cat ./workspace/datasets/fasttext/products.txt |  cut -c 10- | sed -e "s/\([.\!?,'/()]\)/ \1 /g" | tr "[:upper:]" "[:lower:]" | sed "s/[^[:alnum:]]/ /g" | tr -s ' ' > ./workspace/datasets/fasttext/normalized_products.txt
    # ./fasttext skipgram -input ./normalized_products.txt -output ./title_model

    # python week2/createContentTrainingData.py --output ./workspace/datasets/fasttext/products.txt --label name

    print("Writing results to %s" % output_file)
    write_bar = tqdm(total=len(total_label_list))
    with open(output_file, 'w') as output:
        for (cat, name) in total_label_list:
            if cat in cat_products and (len(cat_products[cat]) > min_products):
                output.write(f'__label__{cat} {name}\n')
            write_bar.update()

    write_bar.clear()
    write_bar.close()
