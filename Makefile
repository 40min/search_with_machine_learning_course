.DEFAULT_GOAL := start
DATA_DIR := $(shell pwd)/workspace/datasets/fasttext

.PHONY: start
start:
	docker-compose -f docker/docker-compose.yml up

.PHONY: stop
stop:
	docker-compose -f docker/docker-compose.yml stop

.PHONY: index
index:
	./index-data.sh -r -p `pwd`/week2/conf/bbuy_products.json

.PHONY: delete
delete:
	./delete-indexes.sh

.PHONY: count
count:
	./count-tracker.sh

.PHONY: track_index_products
track_index_products:
	tail -f logs/index_products.log

.PHONY: track_index_queries
track_index_queries:
	tail -f logs/index_queries.log

.PHONY: ltr
ltr:
	./ltr-end-to-end.sh -y

.PHONY: generate
generate:
	python `pwd`/week2/createContentTrainingData.py --label id --min_products 500 --output ${DATA_DIR}/labeled_products.txt

.PHONY: shuffle
shuffle:
	bash -c "shuf ${DATA_DIR}/labeled_products.txt  --random-source=<(seq 99999) > ${DATA_DIR}/shuffled_labeled_products.txt"

.PHONY: normalize
normalize:
	cat ${DATA_DIR}/shuffled_labeled_products.txt |sed -e "s/\([.\!?,'/()]\)/ \1 /g" | tr "[:upper:]" "[:lower:]" | sed "s/[^[:alnum:]_]/ /g" | tr -s ' ' > ${DATA_DIR}/normalized_labeled_products.txt

.PHONY: split
split:
	head -10000 ${DATA_DIR}/normalized_labeled_products.txt > ${DATA_DIR}/training_data.txt && \
	tail -10000 ${DATA_DIR}/normalized_labeled_products.txt > ${DATA_DIR}/test_data.txt
	wc ${DATA_DIR}/test_data.txt
	wc ${DATA_DIR}/training_data.txt

.PHONY: train
train:
	fasttext supervised -input ${DATA_DIR}/training_data.txt -output ${DATA_DIR}/model -lr 1.0 -epoch 25 -wordNgrams 2

.PHONY: test_model
test_model:
	fasttext test ${DATA_DIR}/model.bin ${DATA_DIR}/test_data.txt

.PHONY: predict
predict:
	fasttext predict ${DATA_DIR}/model.bin -

.PHONY: run
run: generate shuffle normalize split train test_model

.PHONY: generate_synonyms_data
generate_synonyms_data:
	python `pwd`/week2/createContentTrainingData.py --label name --transform --output ${DATA_DIR}/products.txt

.PHONY: normalize_synonyms_data
normalize_synonyms_data:
	cat ${DATA_DIR}/products.txt | sed -e "s/\([.\!?,'/()]\)/ \1 /g" | tr "[:upper:]" "[:lower:]" | sed "s/[^[:alnum:]]/ /g" | tr -s ' ' > ${DATA_DIR}/normalized_products.txt

.PHONY: train_synonyms
train_synonyms:
	fasttext skipgram -input ${DATA_DIR}/normalized_products.txt -output ${DATA_DIR}/title_model -minCount 7 -epoch 25

.PHONY: predict_synonyms
predict_synonyms:
	fasttext nn ${DATA_DIR}/title_model.bin

.PHONY: top_words
top_words:
	cat ${DATA_DIR}/normalized_products.txt | tr " " "\n" | grep "...." | sort | uniq -c | sort -nr | head -1000 | grep -oE '[^ ]+$'' > ${DATA_DIR}/top_words.txt

.PHONY: top_words_synonyms
top_words_synonyms:
	python `pwd`/week2/generateSynonyms.py

.PHONY: run_synonyms
run_synonyms: generate_synonyms_data normalize_synonyms_data train_synonyms top_words top_words_synonyms

.PHONY: copy_synonyms_to_container
copy_synonyms_to_container:
	docker cp ${DATA_DIR}/synonyms.csv opensearch-node1:/usr/share/opensearch/config/synonyms.csv

.PHONY: shell
shell:
	@docker-compose -f docker/docker-compose.yml  exec opensearch-node1 /bin/bash

.PHONY: generate_reviews_data
generate_reviews_data:
	python week2/createReviewLabels.py --output ${DATA_DIR}/output_reviews.fasttext


.PHONY: shuffle_reviews_data
shuffle_reviews_data:
	bash -c "shuf ${DATA_DIR}/output_reviews.fasttext  --random-source=<(seq 99999) > ${DATA_DIR}/shuffled_output_reviews.fasttext"

.PHONY: normalize_reviews_data
normalize_reviews_data:
	cat ${DATA_DIR}/shuffled_output_reviews.fasttext |sed -e "s/\([.\!?,'/()]\)/ \1 /g" | tr "[:upper:]" "[:lower:]" | sed "s/[^[:alnum:]_]/ /g" | tr -s ' ' > ${DATA_DIR}/normalized_output_reviews.fasttext

.PHONY: split_reviews_data
split_reviews_data:
	head -10000 ${DATA_DIR}/normalized_output_reviews.fasttext > ${DATA_DIR}/reviews_training_data.txt && \
	tail -10000 ${DATA_DIR}/normalized_output_reviews.fasttext > ${DATA_DIR}/reviews_test_data.txt
	wc ${DATA_DIR}/reviews_test_data.txt
	wc ${DATA_DIR}/reviews_training_data.txt

.PHONY: train_reviews
train_reviews:
	fasttext supervised -input ${DATA_DIR}/reviews_training_data.txt -output ${DATA_DIR}/reviews_model -lr 1.0 -epoch 25 -wordNgrams 2

.PHONY: test_reviews_model
test_reviews_model:
	fasttext test ${DATA_DIR}/reviews_model.bin ${DATA_DIR}/reviews_test_data.txt

.PHONY: predict_reviews
predict_reviews:
	fasttext predict ${DATA_DIR}/reviews_model.bin -

.PHONY: run_reviews
run_reviews: generate_reviews_data shuffle_reviews_data normalize_reviews_data split_reviews_data train_reviews test_reviews_model
