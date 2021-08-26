FEATURE_KEY = 'title'
LABEL_KEY = 'source'
N_CLASSES = 3
HUB_URL = "https://tfhub.dev/google/nnlm-en-dim50/2"
HUB_DIM = 50
N_NEURONS = 16
TRAIN_BATCH_SIZE = 5
EVAL_BATCH_SIZE = 5
MODEL_NAME = 'tfx_title_classifier'


def transformed_name(key):
    return key + '_xf'
