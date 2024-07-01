
import os
import sys
import math
import pickle
import configparser
from nltk.corpus import stopwords

from contextualized_topic_models.models.ctm import CombinedTM
from contextualized_topic_models.utils.data_preparation import TopicModelDataPreparation
from contextualized_topic_models.utils.data_preparation import bert_embeddings_from_file

from data_handler import TopicModelingToolkitDataHandler, load_documents_from_sqlite

STOPWORDS = stopwords.words('english')

class CTMModel:
    def __init__(self, docs_clean: list, trained_model=None):
        os.environ["TOKENIZERS_PARALLELISM"] = "false"
        
        self.documents_clean = docs_clean
        self.trained_model = trained_model
        self.DEFAULT_MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "CTM_model")
        self.DEFAULT_MODEL_FILENAME = "CTM_model.pickle"
        self.DEFAULT_DOC_IDX_ID_MAP_FILENAME = "CTM_document_map.pickle"
        self.DOCUMENT_IDX_ID_MAP = None
        self.DOCUMENT_IDX_TOPIC_MAP = []

        # Create model directory
        if not os.path.exists(self.DEFAULT_MODEL_PATH):
            os.makedirs(self.DEFAULT_MODEL_PATH)
    
    def train_model(self, load_trained_model=True, offload_trained_model=True):
        def offload_model():
            if not os.path.exists(self.DEFAULT_MODEL_PATH):
                os.makedirs(self.DEFAULT_MODEL_PATH)
            offload_model_absp = os.path.join(self.DEFAULT_MODEL_PATH, self.DEFAULT_MODEL_FILENAME)
            with open(offload_model_absp, "wb") as wf:
                pickle.dump(self.trained_model, wf)

            offload_doc_map_absp = os.path.join(
                self.DEFAULT_MODEL_PATH, self.DEFAULT_DOC_IDX_ID_MAP_FILENAME)
            with open(offload_doc_map_absp, "wb") as wf:
                pickle.dump(self.DOCUMENT_IDX_ID_MAP, wf)

            print(f" - Trained Model Off-loaded ({offload_model_absp})...")
            print(f" - Trained Document Map Off-loaded ({offload_doc_map_absp})...")

        def load_model():
            try:
                print(
                    f"Loading model {os.path.join(self.DEFAULT_MODEL_PATH, self.DEFAULT_MODEL_FILENAME)}")
                with open(os.path.join(self.DEFAULT_MODEL_PATH, self.DEFAULT_MODEL_FILENAME), 'rb') as rf:
                    self.trained_model = pickle.load(rf)
                with open(os.path.join(self.DEFAULT_MODEL_PATH, self.DEFAULT_DOC_IDX_ID_MAP_FILENAME), 'rb') as rf:
                    self.DOCUMENT_IDX_ID_MAP = pickle.load(rf)
                return True
            except Exception as ex:
                print(ex.__traceback__)
                return False
        
        # Load model
        load_success = False
        if load_trained_model:
            load_success = load_model()
            if not load_success:
                print("Model loading failed..."); exit()

        # If model load failed || model not loaded
        if not load_trained_model or not load_success:
            print("Training model...")
            
            NUMBER_OF_TOPICS = 25
            qt = TopicModelDataPreparation("all-mpnet-base-v2")
            training_dataset = qt.fit(text_for_contextual=self.documents_clean, text_for_bow=self.documents_clean)
            ctm = CombinedTM(bow_size=len(qt.vocab), contextual_size=768, n_components=NUMBER_OF_TOPICS, num_epochs=10) # 50 topics
            ctm.fit(training_dataset) # run the model
            
            testing_dataset = qt.transform(text_for_contextual=lines, text_for_bow=lines)
            res = ctm.get_doc_topic_distribution(testing_dataset, n_samples=20)
            for r in res:
                self.DOCUMENT_IDX_TOPIC_MAP.append(list(r).index(max(list(r))))
            self.trained_model = ctm
            
        # Save trained model (if model is loaded, don't offload it again)
        if not load_trained_model and offload_trained_model:
            offload_model()
            
    def get_topics(self):
        return [v for _, v in self.trained_model.get_topics().items()]
    
    def get_doc_topic(self):
        return self.DOCUMENT_IDX_TOPIC_MAP
            
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
    SAMPLE_COUNT = 100

    print(f"""
[Topic Modeling Toolkit] CTM Model Settings
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
        # Loading documents from SQLite DB
        id_abs_list, idx_id_map = load_documents_from_sqlite()

        # Cleaning documents
        bert_handler = TopicModelingToolkitDataHandler(sample_doc_count=SAMPLE_COUNT)
        lines = bert_handler.multithreaded_clean_docs(id_abs_list)

    ctm = CTMModel(lines)
    ctm.train_model(load_model, save_model)
    
    for idx, i in enumerate(ctm.get_doc_topic()):
        s = ", ".join(ctm.get_topics()[i])
        print(f"[Document {idx} - Topic {i}] {s}")

    


                        




