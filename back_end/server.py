import os
import sqlite3
import configparser
import time

from TopicModelingKit.src.searcher.searcher import Searcher
from TopicModelingKit.src.models.BERTopic import BertopicModel
from TopicModelingKit.src.models.data_handler import TopicModelingToolkitDataHandler, load_documents_from_sqlite

from flask_cors import CORS
from flask import Flask, abort, jsonify, g, request
app = Flask(__name__)
CORS(app)


# ====================================
# =====| Config File Loading |========
# ====================================

CONFIGPATH = os.path.join(os.path.dirname(
    __file__), "TopicModelingKit", "config.ini")
config = configparser.ConfigParser()
config.read(CONFIGPATH)

# =======================================
# =====| Model Loading/Training |========
# =======================================

load_model = config.getboolean('model-training', 'loadModel')
save_model = config.getboolean('model-training', 'saveModel')


# Train model
if not load_model:

    # Loading documents from SQLite DB
    id_abs_list, idx_id_map = load_documents_from_sqlite()

    # Cleaning documents
    bert_handler = TopicModelingToolkitDataHandler(threads=10, sample_doc_count=None)
    lines = bert_handler.multithreaded_clean_docs(id_abs_list)

# Model loaded, not trained
else:
    idx_id_map = None  # Will be loaded along with the model
    lines = []


print(f"Training model with {len(lines)} documents...")
bm = BertopicModel(lines)
bm.DOCUMENT_IDX_ID_MAP = idx_id_map
bm.train_model(
    num_topics=(1, 1),
    load_trained_model=load_model,
    offload_trained_model=save_model
)

# ====================================
# =====| Database Connection |========
# ====================================


def get_db():
    """Opens a new database connection."""
    db = getattr(g, '_database', None)
    if db is None:
        config = configparser.ConfigParser()
        config.read(CONFIGPATH)
        database_path = config['dataset']['pathOfDatabase']
        database = os.path.join(os.path.dirname(__file__), database_path)
        db = g._database = sqlite3.connect(database)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    """Closes the database again at the end of the request."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# ====================================
# =======| Helper Functions |=========
# ====================================


# def get_metadata_fields():
#     config = configparser.ConfigParser()
#     config.read(CONFIGPATH)
#     metadata_list = config["document"]["metadata"]
#     names = []
#     for item in metadata_list.strip("[]").split("}, "):
#         # Add back the curly brace for eval parsing
#         if not item.endswith("}"):
#             item += "}"
#         # Store the name in separate lists
#         for key, value in eval(item).items():
#             if key == "name":
#                 names.append(value)
#     return names
def get_metadata_fields():
    if not hasattr(get_metadata_fields, 'metadata_fields'):
        config = configparser.ConfigParser()
        config.read(CONFIGPATH)
        metadata_list = config["document"]["metadata"]
        names = []
        for item in metadata_list.strip("[]").split("}, "):
            # Add back the curly brace for eval parsing
            if not item.endswith("}"):
                item += "}"
            # Store the name in separate lists
            for key, value in eval(item).items():
                if key == "name":
                    names.append(value)
        get_metadata_fields.metadata_fields = names

    return get_metadata_fields.metadata_fields


# def get_document_metadata(data):
#     metadata_fields = get_metadata_fields()
#     return {
#         field: data[field]
#         for field in metadata_fields
#     }


def docs_query(ids: list, sort: str = None, order: str = None, filter_field: str = None, filter_input: str = None):
    """A helper function that returns a list of documents in the database that match the given list of ids."""
    cur = get_db().cursor()
    sql_query = "SELECT * FROM Dataset WHERE id IN ({})".format(
        ','.join('?'*len(ids)))
    params = ids

    if filter_field and filter_input:
        sql_query += f" AND {filter_field} LIKE ?"
        params += (f"%{filter_input}%",)

    if sort and order:
        sql_query += f" ORDER BY {sort} {order}"

    cur.execute(sql_query, tuple(params))
    data = cur.fetchall()
    metadata_fields = get_metadata_fields()
    response = []
    for row in data:
        metadata = {field: row[field] for field in metadata_fields}
        response.append({
            'id': row['id'],
            'metadata': metadata,
        })
    return jsonify(response)


# ====================================
# =============| APIs |===============
# ====================================

@app.route('/api/docs')
def api_get_docs():
    """Gets all the documents in the database."""
    cur = get_db().cursor()
    cur.execute('SELECT * FROM Dataset')
    data = cur.fetchmany(3000)
    metadata_fields = get_metadata_fields()
    response = []
    for row in data:
        metadata = {field: row[field] for field in metadata_fields}
        response.append({
            'id': row['id'],
            'metadata': metadata,
        })
    return jsonify(response)


@app.route('/api/search')
def api_search():
    """Returns a list of documents that match the given query."""
    query = request.args.get('q')
    sort = request.args.get('sort')
    order = request.args.get('order')
    filter_field = request.args.get('filter_field')
    filter_input = request.args.get('filter_input')

    searcher = Searcher()
    # searcher.setUpIndex()
    result = searcher.search_BM25(100, query)

    return docs_query(result, sort, order, filter_field, filter_input)


@app.route('/api/get_allow_sort')
def api_get_allow_sort():
    """ Returns a list of fields that can be used to sort the documents """
    config = configparser.ConfigParser()
    config.read(CONFIGPATH)

    document_section = config['document']
    metadata = eval(document_section['metadata'])

    allow_sort_fields = []
    for field in metadata:
        if field.get('allow_sort'):
            allow_sort_fields.append(field['name'])

    return jsonify(allow_sort_fields)


@app.route('/api/get_allow_filter')
def api_get_allow_filter():
    """ Returns a list of fields that can be used to filter the documents """
    config = configparser.ConfigParser()
    config.read(CONFIGPATH)

    document_section = config['document']
    metadata = eval(document_section['metadata'])

    allow_filter_fields = []
    for field in metadata:
        if field.get('allow_filter'):
            allow_filter_fields.append(field['name'])

    return jsonify(allow_filter_fields)


@app.route('/api/get_top_region')
def api_get_top_region():
    """Returns the list of fields that are displayed at the top of the document details page."""
    config = configparser.ConfigParser()
    config.read(CONFIGPATH)

    display_section = config['display']
    top_region = display_section['topRegion']

    return top_region


@app.route('/api/get_bottom_region')
def api_get_bottom_region():
    """Returns the list of fields that are displayed at the bottom of the document details page."""
    config = configparser.ConfigParser()
    config.read(CONFIGPATH)

    display_section = config['display']
    top_region = display_section['bottomRegion']

    return top_region


@app.route('/api/document/<string:document_id>')
def api_get_doc_by_id(document_id):
    """Returns a single document based on its ID."""
    cur = get_db().cursor()
    cur.execute("SELECT * FROM Dataset WHERE id = ?", [document_id])
    data = cur.fetchone()
    metadata_fields = get_metadata_fields()
    if not data:
        abort(404)
    response = {
        'id': data['id'],
        'metadata': {field: data[field] for field in metadata_fields}
    }
    return jsonify(response)


@app.route('/api/get_all_labels')
def api_all_labels():
    res = []
    all_labels = bm.get_all_topics_labels()
    for idx in range(1, len(all_labels)):
        res.append({"id": idx, "topic_list": all_labels[idx]})
    return jsonify(res)


@app.route('/api/labels')
def api_get_labels():
    query_string = request.args.get('topic_query')
    print("query_string: ", query_string)
    doc_labels = bm.query_documents_labels(
        query_string,
        topic_count=5
    )

    return jsonify(doc_labels)


@app.route('/api/get_similar_topics')
def api_get_simliar_topics():
    doc_id = request.args.get('doc_id')

    doc_idx = None
    for k, v in bm.DOCUMENT_IDX_ID_MAP.items():
        if int(v) == int(doc_id):
            doc_idx = int(k)

    # print(f"doc_id: {doc_id}, doc_idx: {doc_idx}")
    topic_id = bm.get_document_topic_map()[doc_idx]
    # print("topic_id: ", topic_id)
    labels = bm.get_topic_words(topic_id)
    # print("labels: ", labels)

    similar_labels = []
    similar_topics, _ = bm.trained_model.find_topics(labels[0], top_n=5)
    for ct, st_id in enumerate(similar_topics):
        if ct > 0:
            tws = bm.get_topic_words(st_id)
            similar_labels.append({'id': st_id, 'topic_list': tws})

    # print("similar_labels: ", similar_labels)
    return jsonify(similar_labels)


@app.route('/api/get_similar_documents')
def api_get_simliar_documents():
    arg_doc_id = request.args.get('doc_id')

    SIMILAR_DOC_COUNT = 20

    doc_idx = None
    for k, v in bm.DOCUMENT_IDX_ID_MAP.items():
        if int(v) == int(arg_doc_id):
            doc_idx = int(k)

    # print(f"doc_id: {arg_doc_id}, doc_idx: {doc_idx}")
    topic_id = bm.get_document_topic_map()[doc_idx]
    # print("topic_id: ", topic_id)
    labels = bm.get_topic_words(topic_id)

    similar_topics_list = []
    for label in labels:
        similar_topics, _ = bm.trained_model.find_topics(label, top_n=2)
        similar_topics_list.append(similar_topics[0])
    similar_topics_list = list(set(similar_topics_list))

    similar_doc_indices = []
    for topic_id in similar_topics_list:
        fetched_similar_doc_indices = bm.get_documents_with_topic_id(topic_id)
        for doc_id in fetched_similar_doc_indices:
            similar_doc_indices.append(doc_id)
    doc_indices = list(set(similar_doc_indices[:SIMILAR_DOC_COUNT+1] if SIMILAR_DOC_COUNT+1 < len(
        similar_doc_indices) else similar_doc_indices))

    doc_ids = [bm.DOCUMENT_IDX_ID_MAP[idx] for idx in doc_indices if str(
        bm.DOCUMENT_IDX_ID_MAP[idx]) != str(arg_doc_id)]
    cur = get_db().cursor()
    sql_query = "SELECT * FROM Dataset WHERE id IN ({})".format(
        ','.join('?' * len(doc_ids)))
    params = doc_ids

    cur.execute(sql_query, tuple(params))
    data = cur.fetchall()
    metadata_fields = get_metadata_fields()
    response = []
    for row in data:
        metadata = {field: row[field] for field in metadata_fields}
        response.append({
            'id': row['id'],
            'metadata': metadata,
        })

    return jsonify(response)


@app.route('/api/get_topic_docs')
def api_query_document():
    topic_id = request.args.get('topic_id')
    sort = request.args.get('sort')
    order = request.args.get('order')
    filter_field = request.args.get('filter_field')
    filter_input = request.args.get('filter_input')

    doc_indices = bm.get_documents_with_topic_id(int(topic_id))

    doc_ids = [bm.DOCUMENT_IDX_ID_MAP[idx] for idx in doc_indices]

    # cur = get_db().cursor()
    # sql_query = "SELECT * FROM Dataset WHERE id IN ({})".format(
    #     ','.join('?' * len(doc_ids)))
    # params = doc_ids

    # cur.execute(sql_query, tuple(params))
    # data = cur.fetchmany(3000)

    # metadata_fields = get_metadata_fields()
    # response = []
    # for row in data:
    #     metadata = {field: row[field] for field in metadata_fields}
    #     response.append({
    #         'id': row['id'],
    #         'metadata': metadata,
    #     })

    # return jsonify(response)
    print("sort: ", sort, "order: ", order,
          "filter_field: ", filter_field, "filter_input: ", filter_input)
    return docs_query(doc_ids, sort, order, filter_field, filter_input)


if __name__ == '__main__':
    app.run(debug=True, port=5050)
