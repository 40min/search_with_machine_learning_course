import os.path
import fasttext

_DATA_DIR = "./workspace/datasets/fasttext"
_MODEL_NAME = "title_model_100.bin"
_TOP_WORDS_LIST = "top_words.txt"
_OUTPUT_FILE = "synonyms.csv"
_SIMILARITY_THRESHOLD = 0.8


if __name__ == '__main__':
    model_fp = os.path.join(_DATA_DIR, _MODEL_NAME)
    top_words_fp = os.path.join(_DATA_DIR, _TOP_WORDS_LIST)
    output_fp = os.path.join(_DATA_DIR, _OUTPUT_FILE)

    if os.path.exists(output_fp):
        os.remove(output_fp)

    model = fasttext.load_model(model_fp)
    with open(top_words_fp, 'r') as top_words:
        with open(output_fp, 'x') as output:
            for line in top_words.readlines():
                synonym_from = line.strip()
                neighbors = model.get_nearest_neighbors(synonym_from)
                good_enough_neighbors = [n[1] for n in neighbors if n[0] > _SIMILARITY_THRESHOLD]
                if good_enough_neighbors:
                    output.write(f"{synonym_from},{','.join(good_enough_neighbors)}\n")
