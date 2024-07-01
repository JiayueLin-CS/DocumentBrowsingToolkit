import os
import sys
import math
import pickle
import configparser
import multiprocessing
from nltk.corpus import stopwords
from bertopic import BERTopic

STOPWORDS = stopwords.words('english')

try:
    from TopicModelingKit.src.database.dataset_dbtool import get_sqlite_conn, load_database_table
except:
    sys.path.append(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))))
    from database.dataset_dbtool import get_sqlite_conn, load_database_table

class TopicModelingToolkitDataHandler:
    def __init__(self, threads=None, sample_doc_count=None):
        self.threads = multiprocessing.cpu_count() if threads == None else threads
        self.sample_doc_count = sample_doc_count + \
            1 if isinstance(sample_doc_count, int) else None

    def multithreaded_clean_docs(self, document_id_list: list):
        """
        Multitheaded data cleaning
        """
        print(f"Cleaning {len(document_id_list) if self.sample_doc_count == None else self.sample_doc_count} documents on {self.threads} threads...")

        res = []
        document_id_list = document_id_list if self.sample_doc_count == None else document_id_list[:self.sample_doc_count]
        partitioned_docs = self.partition_list(document_id_list, self.threads)
        with multiprocessing.Pool(self.threads) as pool:
            result = pool.map(self.clean_doc, partitioned_docs)
        result = [sub_bundle for sub_bundle in [bundle for bundle in result]]
        for sub_bundle in result:
            for idx, doc in enumerate(sub_bundle):
                if isinstance(doc, tuple) and isinstance(doc[1], str):
                    res.append(doc)

        return [doc[1] for doc in sorted(res, key=lambda x: x[0])]

    def clean_doc(self, docs: list):
        # print(f" - [PID {os.getpid()}] Forked process started...")

        clean_document_id_list = []
        for i in range(len(docs)):
            document_id = docs[i][0]
            document_abs = docs[i][1]

            line_tokens = document_abs.lower().split()
            for sw in STOPWORDS:
                line_tokens = [token for token in line_tokens if token != sw]
            clean_document_id_list.append((document_id, " ".join(line_tokens)))
        return clean_document_id_list

    def progressbar(self, it, prefix="", size=50, out=sys.stdout): 
        count = len(it)

        def show(j):
            x = int(size*j/count)
            print("{}[{}{}] {}/{}".format(prefix, "#"*x, "." *
                  (size-x), j, count), end='\r', file=out, flush=True)
        show(0)
        for i, item in enumerate(it):
            yield item
            show(i+1)
        print("\n", flush=True, file=out)

    def partition_list(self, input_list, segment_count):
        chunk_size = math.ceil(len(input_list) / segment_count)
        for i in range(0, len(input_list), chunk_size):
            yield input_list[i: i+chunk_size]
            
def load_documents_from_sqlite():
    """
    Load all documents from the SQLite databases.

    doc_id_map, idx_id_map = load_documents_from_sqlite()
    lines = list(doc_id_map.values())

    :return:
        - doc_id_list   : List mapping between          [(doc_id1, abstract1), (doc_id2, abstract_2)...]
            - Used to ensure document index order during the multi-threaded data cleaning process

        - idx_id_map    : Dictionary mapping between    {idx_0: doc_id1, idx_1: doc_id2 ...}
            - Used to identify the ID of the document from the Database based on the document's index
    """
    db_conn = get_sqlite_conn()
    ids = load_database_table(db_conn, column="id", table_name="Dataset")
    abstracts = load_database_table(
        db_conn, column="abstract", table_name="Dataset")

    assert (len(ids) == len(abstracts))
    id_abs_list = [(ids[i], abstracts[i]) for i in range(len(ids))]

    idx_id_map = dict()
    for idx, id in enumerate(ids):
        idx_id_map[idx] = id

    return id_abs_list, idx_id_map