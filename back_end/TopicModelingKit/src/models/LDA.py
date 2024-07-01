


import os
import sys
import math
import pickle
import configparser
from nltk.corpus import stopwords

from nltk.stem import WordNetLemmatizer  
from sklearn.feature_extraction.text import TfidfVectorizer
from data_handler import TopicModelingToolkitDataHandler, load_documents_from_sqlite

STOPWORDS = stopwords.words('english')

class LDAModel:
    def __init__(self, docs_clean: list, trained_model=None):
        self.documents = docs_clean
        self.trained_model = trained_model
        self.DEFAULT_MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "LDA_model")
        self.DEFAULT_MODEL_FILENAME = "LDA_model.pickle"
        self.DEFAULT_DOC_IDX_ID_MAP_FILENAME = "LDA_document_map.pickle"
        self.DOCUMENT_IDX_ID_MAP = None

        # Create model directory
        if not os.path.exists(self.DEFAULT_MODEL_PATH):
            os.makedirs(self.DEFAULT_MODEL_PATH)
            
    def train_model(self, load_model, save_model):
        vect = TfidfVectorizer(stop_words=STOPWORDS, max_features=1000)
        vect_text = vect.fit_transform(self.documents)
        
        NUM_OF_TOPICS = 100
        from sklearn.decomposition import LatentDirichletAllocation
        lda_model=LatentDirichletAllocation(
            n_components=NUM_OF_TOPICS,
            learning_method='online',
            random_state=42,
            max_iter=1
        )
        lda_top=lda_model.fit_transform(vect_text)


        topic_dict = dict()
        vocab = vect.get_feature_names_out()
        for i, comp in enumerate(lda_model.components_):
            vocab_comp = zip(vocab, comp)
            sorted_words = sorted(vocab_comp, key= lambda x:x[1], reverse=True)[:10]
            topic_dict[i] = sorted_words

        for doc_idx, doc in enumerate(lda_top):
            for i, topic in enumerate(doc):
                if topic*100 > 50:
                    s = ", ".join([w[0] for w in topic_dict[i]])
                    print(f"[Document {doc_idx} - Topic {i} (acc {round(topic, 2)})] {s}")
                
                
    
if __name__ == "__main__":
    print("Loading documents...")

    CONFIGPATH = os.path.join(os.path.dirname(
        os.path.dirname(os.path.dirname(__file__))), "config.ini")
    config = configparser.ConfigParser()
    config.read(CONFIGPATH)

    # =======================================
    # =====| Model Loading/Training |========
    # =======================================

    load_model = config.getboolean('model-training', 'loadModel')
    save_model = config.getboolean('model-training', 'saveModel')
    SAMPLE_COUNT = None

    print(f"""
[Topic Modeling Toolkit] LDA Model Settings
- [Load Model]: {load_model}
- [Save Model]: {save_model}
- [Sample Count]: {SAMPLE_COUNT}       
          """)
    # if input("Continue? [y/n]: ").lower() != 'y': exit()

    if not load_model:
        # Loading documents from SQLite DB
        id_abs_list, idx_id_map = load_documents_from_sqlite()

        # Cleaning documents
        bert_handler = TopicModelingToolkitDataHandler(sample_doc_count=SAMPLE_COUNT)
        lines = bert_handler.multithreaded_clean_docs(id_abs_list)
    else:
        lines = []

    print("\nTraining model...")
    ctm = LDAModel(lines)
    ctm.train_model(load_model, save_model)
    