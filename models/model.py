from sentence_transformers import SentenceTransformer

def load_model_and_tokenizer():
    # Load a pretrained model — you will later replace this with your trained version
    model = SentenceTransformer('all-MiniLM-L6-v2')
    tokenizer = None  # Optional, based on model
    return model, tokenizer
