# A simple client for querying driven by user input on the command line.  Has hooks for the various
# weeks (e.g. query understanding).  See the main section at the bottom of the file
from typing import Optional, Any

import fasttext
from opensearchpy import OpenSearch
import warnings

from sentence_transformers import SentenceTransformer

warnings.filterwarnings("ignore", category=FutureWarning)
import argparse
import json
import os
from getpass import getpass
from urllib.parse import urljoin
import pandas as pd
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(format='%(levelname)s:%(message)s')

# expects clicks and impressions to be in the row
def create_prior_queries_from_group(
        click_group):  # total impressions isn't currently used, but it mayb worthwhile at some point
    click_prior_query = ""
    # Create a string that looks like:  "query": "1065813^100 OR 8371111^89", where the left side is the doc id and the right side is the weight.  In our case, the number of clicks a document received in the training set
    if click_group is not None:
        for item in click_group.itertuples():
            try:
                click_prior_query += "%s^%.3f  " % (item.doc_id, item.clicks / item.num_impressions)

            except KeyError as ke:
                pass  # nothing to do in this case, it just means we can't find priors for this doc
    return click_prior_query


# expects clicks from the raw click logs, so value_counts() are being passed in
def create_prior_queries(doc_ids, doc_id_weights,
                         query_times_seen):  # total impressions isn't currently used, but it mayb worthwhile at some point
    click_prior_query = ""
    # Create a string that looks like:  "query": "1065813^100 OR 8371111^89", where the left side is the doc id and the right side is the weight.  In our case, the number of clicks a document received in the training set
    click_prior_map = ""  # looks like: '1065813':100, '8371111':809
    if doc_ids is not None and doc_id_weights is not None:
        for idx, doc in enumerate(doc_ids):
            try:
                wgt = doc_id_weights[doc]  # This should be the number of clicks or whatever
                click_prior_query += "%s^%.3f  " % (doc, wgt / query_times_seen)
            except KeyError as ke:
                pass  # nothing to do in this case, it just means we can't find priors for this doc
    return click_prior_query


# Hardcoded query here.  Better to use search templates or other query config.
def create_query(user_query, click_prior_query, filters, sort="_score", sortDir="desc", size=10, source=None, use_synonyms=False, category_matchers=None):
    name_field = "name.synonyms" if use_synonyms else "name"
    query_obj = {
        'size': size,
        "sort": [
            {sort: {"order": sortDir}}
        ],
        "query": {
            "function_score": {
                "query": {
                    "bool": {
                        "must": [

                        ],
                        "should": [  #
                            {
                                "match": {
                                    name_field: {
                                        "query": user_query,
                                        "fuzziness": "1",
                                        "prefix_length": 2,
                                        # short words are often acronyms or usually not misspelled, so don't edit
                                        "boost": 0.01
                                    }
                                }
                            },
                            {
                                "match_phrase": {  # near exact phrase match
                                    "name.hyphens": {
                                        "query": user_query,
                                        "slop": 1,
                                        "boost": 50
                                    }
                                }
                            },
                            {
                                "multi_match": {
                                    "query": user_query,
                                    "type": "phrase",
                                    "slop": "6",
                                    "minimum_should_match": "2<75%",
                                    "fields": [f"{name_field}^10", "name.hyphens^10", "shortDescription^5",
                                               "longDescription^5", "department^0.5", "sku", "manufacturer", "features",
                                               "categoryPath"]
                                }
                            },
                            {
                                "terms": {
                                    # Lots of SKUs in the query logs, boost by it, split on whitespace so we get a list
                                    "sku": user_query.split(),
                                    "boost": 50.0
                                }
                            },
                            {  # lots of products have hyphens in them or other weird casing things like iPad
                                "match": {
                                    "name.hyphens": {
                                        "query": user_query,
                                        "operator": "OR",
                                        "minimum_should_match": "2<75%"
                                    }
                                }
                            }
                        ],
                        "minimum_should_match": 1,
                        "filter": filters  #
                    }
                },
                "boost_mode": "multiply",  # how _score and functions are combined
                "score_mode": "sum",  # how functions are combined
                "functions": [
                    {
                        "filter": {
                            "exists": {
                                "field": "salesRankShortTerm"
                            }
                        },
                        "gauss": {
                            "salesRankShortTerm": {
                                "origin": "1.0",
                                "scale": "100"
                            }
                        }
                    },
                    {
                        "filter": {
                            "exists": {
                                "field": "salesRankMediumTerm"
                            }
                        },
                        "gauss": {
                            "salesRankMediumTerm": {
                                "origin": "1.0",
                                "scale": "1000"
                            }
                        }
                    },
                    {
                        "filter": {
                            "exists": {
                                "field": "salesRankLongTerm"
                            }
                        },
                        "gauss": {
                            "salesRankLongTerm": {
                                "origin": "1.0",
                                "scale": "1000"
                            }
                        }
                    },
                    {
                        "script_score": {
                            "script": "0.0001"
                        }
                    }
                ]

            }
        }
    }

    if category_matchers:
        query_obj["query"]["function_score"]["query"]["bool"]["should"].extend(category_matchers)

    if click_prior_query is not None and click_prior_query != "":
        query_obj["query"]["function_score"]["query"]["bool"]["should"].append({
            "query_string": {
                # This may feel like cheating, but it's really not, esp. in ecommerce where you have all this prior data,  You just can't let the test clicks leak in, which is why we split on date
                "query": click_prior_query,
                "fields": ["_id"]
            }
        })
    if user_query == "*" or user_query == "#":
        # replace the bool
        try:
            query_obj["query"] = {"match_all": {}}
        except:
            print("Couldn't replace query for *")
    if source is not None:  # otherwise use the default and retrieve all source
        query_obj["_source"] = source
    return query_obj


_model = None
QUERY_CLASSIFY_THRESHOLD = 0.5
CATEGORY_BOOST = 100
CATEGORIES_BELOW_THRESHOLD_BOOST = 50


def get_model():
    global _model
    _DATA_DIR = "./workspace/datasets/fasttext"
    _MODEL_NAME = "query_category_model100.bin"

    if not _model:
        model_fp = os.path.join(_DATA_DIR, _MODEL_NAME)
        _model = fasttext.load_model(model_fp)
    return _model


def classify_query(user_query: str) -> tuple[Optional[str], Optional[list[str]]]:

    below_threshold_categories = []
    summary_scores_of_below_threshold = 0

    model = get_model()
    categories, scores = model.predict(user_query, threshold=0, k=10)

    for labeled_category, score in zip(categories, scores):
        score = float(score)
        category = labeled_category.replace("__label__", "")
        if score > QUERY_CLASSIFY_THRESHOLD:
            return category, None

        summary_scores_of_below_threshold += score
        below_threshold_categories.append(category)
        if summary_scores_of_below_threshold > QUERY_CLASSIFY_THRESHOLD:
            return None, below_threshold_categories

    return None, None


_sentence_model = None

def get_sentence_model():
    global _sentence_model
    if not _sentence_model:
        _sentence_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    return _sentence_model


def create_vector_query(user_query: str, num_results: int, source: list[str]) -> dict[str, Any]:
    embeddings = get_sentence_model().encode([user_query])
    query_embeddings = list(embeddings[0])
    query = {
        "_source": source,
        "size": num_results,
        "query": {
            "bool": {
                "should": [
                    {
                        "knn": {
                            "name_vector": {
                                "vector": query_embeddings,
                                "k": num_results
                            }
                        }
                    },
                    {
                        "knn": {
                            "description_vector": {
                                "vector": query_embeddings,
                                "k": num_results
                            }
                        }
                    }
                ]
            }
        }
    }

    return query



def search(
        client,
        user_query,
        index="bbuy_products",
        sort="_score",
        sortDir="desc",
        use_synonyms=False,
        filter_on_categories=False,
        boost_categories=False,
        use_vectors=False,
):
    #### W3: classify the query
    filters = []
    category_matchers = []
    top_category = None
    below_threshold_cat = []

    if use_vectors:
        query_obj = create_vector_query(
            user_query,
            num_results=10,
            source=["name", "shortDescription"],
        )
    else:
        if filter_on_categories or boost_categories:
            top_category, below_threshold_cat = classify_query(user_query)

        if filter_on_categories:
            #### W3: create filters and boosts
            if top_category:
                filters.append({"term": {"categoryPathIds": top_category}})
            elif below_threshold_cat:
                filters.append({"terms": {"categoryPathIds": below_threshold_cat}})
        elif boost_categories:
            if top_category:
                category_matchers.append({"term": {"categoryPathIds": {"value": top_category, "boost": CATEGORY_BOOST}}})
            elif below_threshold_cat:
                category_matchers.append({"terms": {"categoryPathIds": below_threshold_cat, "boost": CATEGORIES_BELOW_THRESHOLD_BOOST}})

        query_obj = create_query(
            user_query,
            click_prior_query=None,
            filters=filters,
            sort=sort,
            sortDir=sortDir,
            source=["name", "shortDescription"],
            use_synonyms=use_synonyms,
            category_matchers=category_matchers
        )


    logging.info(query_obj)
    response = client.search(query_obj, index=index)
    if response and response['hits']['hits'] and len(response['hits']['hits']) > 0:
        hits = response['hits']['hits']
        print(json.dumps(response, indent=2))


if __name__ == "__main__":
    host = 'localhost'
    port = 9200
    auth = ('admin', 'admin')  # For testing only. Don't store credentials in code.
    parser = argparse.ArgumentParser(description='Build LTR.')
    general = parser.add_argument_group("general")
    general.add_argument("-i", '--index', default="bbuy_products",
                         help='The name of the main index to search')
    general.add_argument("-s", '--host', default="localhost",
                         help='The OpenSearch host name')
    general.add_argument("-p", '--port', type=int, default=9200,
                         help='The OpenSearch port')
    general.add_argument('--user',
                         help='The OpenSearch admin.  If this is set, the program will prompt for password too. If not set, use default of admin/admin')
    general.add_argument("-y", "--synonyms", action="store_true", help='Use synonyms')
    general.add_argument("-f", "--catfilter", action="store_true", help='Use filtering on inferred categories')
    general.add_argument("-b", "--catboost", action="store_true", help='Use boosting of inferred categories')
    general.add_argument("-v", "--vectors", action="store_true", help='Use vector search')

    args = parser.parse_args()

    if len(vars(args)) == 0:
        parser.print_usage()
        exit()

    host = args.host
    port = args.port
    if args.user:
        password = getpass()
        auth = (args.user, password)
    use_synonyms = True if args.synonyms else False
    filter_on_categories = True if args.catfilter else False
    boost_categories = True if args.catboost else False
    use_vectors = True if args.vectors else False

    base_url = "https://{}:{}/".format(host, port)
    opensearch = OpenSearch(
        hosts=[{'host': host, 'port': port}],
        http_compress=True,  # enables gzip compression for request bodies
        http_auth=auth,
        # client_cert = client_cert_path,
        # client_key = client_key_path,
        use_ssl=True,
        verify_certs=False,  # set to true if you have certs
        ssl_assert_hostname=False,
        ssl_show_warn=False,

    )

    index_name = args.index
    query_prompt = "\nEnter your query (type 'Exit' to exit or hit ctrl-c):"
    print(query_prompt)
    while True:
        query = input().rstrip()
        if query == "exit":
            break
        search(
            client=opensearch,
            user_query=query,
            index=index_name,
            use_synonyms=use_synonyms,
            filter_on_categories=filter_on_categories,
            boost_categories=boost_categories,
            use_vectors=use_vectors,
        )

        print(query_prompt)
    