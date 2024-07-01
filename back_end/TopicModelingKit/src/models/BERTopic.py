# from TopicModelingKit.src.database.dataset_dbtool import get_sqlite_conn, load_database_table
import os
import sys
import math
import pickle
import configparser
import multiprocessing
from nltk.corpus import stopwords
from bertopic import BERTopic

from .data_handler import TopicModelingToolkitDataHandler, load_documents_from_sqlite

class BertopicModel:
    def __init__(self, docs: list, trained_model=None):
        self.documents = docs
        self.trained_model = trained_model
        self.DEFAULT_MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bertopic_model_bk")
        self.DEFAULT_MODEL_FILENAME = "bertopic_model.pickle"
        self.DEFAULT_DOC_IDX_ID_MAP_FILENAME = "bertopic_document_map.pickle"

        self.DOCUMENT_IDX_ID_MAP = None

        # Create model directory
        if not os.path.exists(self.DEFAULT_MODEL_PATH):
            os.makedirs(self.DEFAULT_MODEL_PATH)

    # ====================================
    # =========| MODEL TRAINING |=========
    # ====================================

    def train_model(self, num_topics=(1, 1), load_trained_model=True, offload_trained_model=True):
        """
        Train/Load BERTopic Model based on the provided (clean) documents

        :param num_topics: The number words for each labels in the topic.
        :param load_trained_model: True to load a train model and False otherwise. Use False to force a model training.
        :param offload_trained_model: True to save the model and False otherwise.  
        """
        def offload_model():
            if not os.path.exists(self.DEFAULT_MODEL_PATH):
                os.makedirs(self.DEFAULT_MODEL_PATH)
            offload_model_absp = os.path.join(
                self.DEFAULT_MODEL_PATH, self.DEFAULT_MODEL_FILENAME)
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
            NUM_OF_TOPICS = 100  # or "auto"
            topic_model = BERTopic(
                language="english", n_gram_range=num_topics, nr_topics=NUM_OF_TOPICS, verbose=True)
            topics, probs = topic_model.fit_transform(self.documents)
            self.trained_model = topic_model

        # Save trained model (if model is loaded, don't offload it again)
        if not load_trained_model and offload_trained_model:
            offload_model()
            

    # ===========================================
    # =========| BASE HELPER FUNCTIONS |=========
    # ===========================================

    def get_document_text(self, document_id):
        """
        Get document text with document ID
        """
        return self.documents[document_id]

    def get_document_topic_map(self):
        """
        Get a map between the document index and its corresponding topic ID 
            :return: A list similar to :
                [1, 1, 0, 2]
                where   doc index 0 = topic ID 1
                        doc index 1 = topic ID 1
                        doc index 2 = topic ID 0
                        doc index 3 = topic ID 2
        """
        return self.trained_model.topics_

    # ==========================================
    # ===========| TOPIC FUNCTIONS |============
    # ==========================================

    def get_topics_list(self, count=None):
        '''
        Get topics list from the trained model.
            Format:
                {
                    1: [ ("computer science", 0.23), ("machine learning", 0.14) ],
                    2: [ ("final fantasy", 0.23), ("overwatch", 0.14) ]
                }
            where 1 and 2 are topic IDs.

        :param count: Return topics count (starting from index 0)
        :return: Topics dictionary with topic IDs (int values) as keys
        '''
        if isinstance(count, int):
            return self.trained_model.get_topics()[:count]
        else:
            return self.trained_model.get_topics()

    def get_topic_details(self, topic_id):
        """
        Get topic content (words, acc) with topic ID
            :param topic_id: The topic ID to retrieve
            :return: List of tuples, each containing (words, acc)
        """
        # return self.trained_model.get_topic(topic_id)
        return self.trained_model.get_topics()[topic_id]

    def get_all_topics_labels(self):
        """
        Get all topic labels for the model.
        """
        topic_ids = sorted(set(self.get_document_topic_map()))
        # print(topic_ids, [d for d in [self.get_topic_words(tid)
        #       for tid in topic_ids]])
        return [d for d in [self.get_topic_words(tid) for tid in topic_ids if tid != -1]]

    def get_topic_words(self, topic_id):
        """
        Get the words corresponded to the given topic
            :param topic_id: The topic ID to search
            :return: A list of words
        """
        topic = self.get_topic_details(topic_id)
        return [i[0] for i in topic]

    # =============================================
    # ===========| DOCUMENT FUNCTIONS |============
    # =============================================
    # Note: All following document operations are based on INDEX only.
    # Use get_document_text() to get the content of the document.

    def get_documents_with_topic_id(self, topic_id: int, count=None):
        """
        Get document IDs with matching given topic ID
            :param topic_id: The topic ID to filter
            :param count: Number of doc IDs to return
            :return: A list of document IDs with the given topic ID
        """
        doc_topic_map = self.get_document_topic_map()
        doc_ids = [_doc_id for _doc_id, _topic_id in enumerate(
            doc_topic_map) if _topic_id == topic_id]
        return doc_ids if count == None else doc_ids[count]

    def query_documents(self, query, topic_count=1, accuracy_threshold=0):
        """
        Query document IDs with a given string.

        :param query: The given query string
        :param topic_count: Number of topics to query
        :param accuracy_threshold: The minimum accuracy required for the document to be added to the list returned 
        """
        similar_topics, similarity = self.trained_model.find_topics(
            query, top_n=topic_count)

        doc_ids = []
        for idx, i in enumerate(similar_topics):
            if similarity[idx] > accuracy_threshold:
                doc_ids.append(self.get_documents_with_topic_id(i))
        return doc_ids

    def query_documents_labels(self, query, topic_count=10, acc_threshold=0):
        """
        Query labels with a given string.

        :param query: The given query string
        :param topic_count: Number of topics to query
        :param accuracy_threshold: The minimum accuracy required for the document to be added to the list returned 
        """
        similar_topics, similarity = self.trained_model.find_topics(
            query, top_n=topic_count)

        # print(similarity)
        res = []
        for idx, i in enumerate(similar_topics):
            if similarity[idx] > acc_threshold:
                res.append({"id": i, "topic_list": [
                           j for j in self.get_topic_words(i)]})

        return res

    def get_similar_documents(self, doc_id: int, num_docs=None):
        """
        Given a document, get similar documents.
        """
        doc_ids = self.trained_model.get_representative_docs(
            self.get_document_topic_map()[doc_id])
        return doc_ids if num_docs == None else doc_ids[:num_docs]





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
[Topic Modeling Toolkit] BERTopic Model Settings
- [Load Model]: {load_model}
- [Save Model]: {save_model}
- [Sample Count]: {SAMPLE_COUNT}       
          """)
    if input("Continue? [y/n]: ").lower() != 'y':
        exit()

    if not load_model:
        # Loading documents from SQLite DB
        id_abs_list, idx_id_map = load_documents_from_sqlite()

        # Cleaning documents
        bert_handler = TopicModelingToolkitDataHandler(sample_doc_count=None)
        lines = bert_handler.multithreaded_clean_docs(id_abs_list)
    else:
        lines = []
        idx_id_map = None

    # Training BERTopic Model
    if SAMPLE_COUNT == None:
        SAMPLE_COUNT = len(lines)

    print(f"Training {SAMPLE_COUNT} documents...")
    bm = BertopicModel(lines[:SAMPLE_COUNT] if SAMPLE_COUNT else lines)
    bm.DOCUMENT_IDX_ID_MAP = idx_id_map
    bm.train_model(
        num_topics=(1, 1),
        load_trained_model=load_model,
        offload_trained_model=save_model
    )

    topic_id = bm.get_document_topic_map()[15]
    labels = bm.get_topic_words(topic_id)

    similar_labels = []
    for label in labels:
        similar_topics, similarity = bm.trained_model.find_topics(
            label, top_n=2)
        for st_id in similar_topics:
            similar_labels += bm.get_topic_words(st_id)

    print(list(set(similar_labels)))
