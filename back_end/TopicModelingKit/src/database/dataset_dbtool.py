import os
import sys
import re
import json
import sqlite3
import argparse
import datetime
from tqdm import tqdm
from termcolor import colored
import configparser

config = configparser.ConfigParser()
config.read("/home/mchenyu/web-app/back_end/TopicModelingKit/config.ini")

JSON_DATASET_ABSPATH = config.get('database', 'jsonDatasetPath').replace("\"", "")
DB_NAME = config.get('database', 'databaseName').replace("\"", "")
DB_PATH = config.get('database', 'databasePath').replace("\"", "")
DATASET_TB_SCHEMA = eval(config.get('database', 'datasetTableSchema'))
DEFAULT_DB_COL_ORDER = [list(v.keys())[0] for v in DATASET_TB_SCHEMA]
NON_OPTIONAL_METADATA_COL = [list(v.keys())[0] for v in DATASET_TB_SCHEMA if v['optional'] == False and v["default"] == False]
OPTIONAL_METADATA_COL = [list(v.keys())[0] for v in DATASET_TB_SCHEMA if v['optional'] == True]

# ===================================================================================================================================================
# | SQL FUNCTIONS | =================================================================================================================================

def get_sqlite_conn():
    '''
    Establish connection to the target SQLite DB.
    :return: SQLite Connection
    '''
    print(os.path.join(DB_PATH, DB_NAME))
    return sqlite3.connect(os.path.join(DB_PATH, DB_NAME))

def drop_all_sqlite_tables(db_conn):
    '''
    Drops SQLite data tables. Used to setup a clean run.
    :param db_conn: SQLite DB connection
    '''
    cur = db_conn.cursor()
    cur.execute("DROP table IF EXISTS Dataset;")
    
    db_conn.commit()
    cur.close()

def create_sqlite_db(db_conn):
    '''
    Create new tables for the SBOM SQLite database with the given schema (if they don't already exit).
    :param db_conn: SQLite DB connection
    '''
    
    schema_list = []
    for col in DATASET_TB_SCHEMA:
        schema_list.append(f"{list(col.keys())[0]}\t{list(col.values())[0]}")
    schema = ",\n\t".join(schema_list)
    create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS Dataset (
            {schema}
        );
    """

    
    cur = db_conn.cursor()
    cur.execute(create_table_sql)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS Metadata (
            version         TEXT NOT NULL DEFAULT '0.0.4',
            db_created_on   DATETIME NOT NULL DEFAULT current_timestamp
        );
    """)
    cur.execute("INSERT INTO metadata DEFAULT VALUES;")
    
    db_conn.commit()
    cur.close()
    
    
def load_database_table(db_conn, column="*", table_name="Dataset"):
    """
    Load the the given table from the database.
    """
    cur = db_conn.cursor()
    sql = f"SELECT {column} FROM {table_name} ORDER BY id ASC;"
    cur.execute(sql)
    return [i[0] for i in cur.fetchall()]

# ===================================================================================================================================================
# | DATASET PARSER FUNCTIONS | ======================================================================================================================

def load_dataset(auto_correct=True):
    dataset_dict = dict()
    with open(JSON_DATASET_ABSPATH, "r") as rf:
        try:
            dataset_dict = json.load(rf)
            return dataset_dict
        except json.decoder.JSONDecodeError:
            pass

    if auto_correct == True:
        with open(JSON_DATASET_ABSPATH, "r") as rf:
            for line in rf.readlines():
                doc = json.loads(line)  
                
                temp = dict()
                
                for col in NON_OPTIONAL_METADATA_COL:
                    try:  temp[col] = doc[col]
                    except:
                        try: temp[col] = doc["metadata"][col]
                        except: temp[col] = "placeholder" 
                
                for col in OPTIONAL_METADATA_COL:
                    try: temp[col] = doc["metadata"][col]
                    except: temp[col] = None
                
                dataset_dict[doc["id"]] = temp
                
        return dataset_dict
    raise Exception("Dataset incorrectly formatted...")
    
def load_to_db(conn, dataset_dict, validate=False):
    cur = conn.cursor()
    
    validate_ct = len(dataset_dict)
    validate_id = dataset_dict.keys()
    
    '''
    INSERT INTO table_name (column1, column2, column3, ...)
    VALUES (value1, value2, value3, ...);
    '''
    print("Generating new database...")
    for doc_id, metadata in tqdm(dataset_dict.items(), ncols=100, desc="Loading records to DB: ", ascii=' ='):
        
        # ===============================
        # ======= | DATA PARSE | ========
        # ===============================
        for k, v in metadata.items():
            if not v: 
                metadata[k] = "None"
            if isinstance(metadata[k], str):
                metadata[k] = metadata[k].replace("\"", "\'")
        metadata["year"] = int(metadata["year"])
        
        # ================================
        # ======= | DATA INSERT | ========
        # ================================
        dataval = [doc_id] + list(metadata.values()) + [datetime.datetime.now().strftime("%Y-%m-%d")]
        values = [f"\"{v}\"" for v in dataval]
        sql = f"INSERT INTO Dataset VALUES({','.join(values)})"
        cur.execute(sql)
        conn.commit()
    print(f" - Database generated at {os.path.join(DB_PATH, DB_NAME)}")
 
 
    # ================================
    # ======= | VALIDATION | =========
    # ================================
    if validate:
        print("\nValidating database's integrity...")
        cur.execute("SELECT count(*) FROM Dataset;")
        row_ct = cur.fetchall()[0][0]
        if row_ct == validate_ct:
            print_res(success=True, type="Count")
        else:
            print_res(success=False, type="Count")
            
        cur.execute("SELECT * FROM Dataset;")
        rows_content = cur.fetchall()
        doc_ids = [doc_id[0] for doc_id in rows_content]
        for i in validate_id:
            if int(i) not in doc_ids:
                print_res(success=False, type="ID"); return
        print_res(success=True, type="ID")
    
    
def print_res(success=True, type=""):
    if success:
        SUCCESS = colored("SUCCESS", "green", attrs=["blink"])
        print(f" - [ {SUCCESS} ] Record {type} Validation")
    else:
        FAILED = colored("FAILED", "red", attrs=["blink"])
        print(f" - [ {FAILED} ] Record {type} Validation")


if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description='Topic Modeling Toolkit Dataset Handler')
    # parser.add_argument('-v', '--verbose', dest="verbose", default=False, action="store_true", help='Verbose output')
    # parser.add_argument('-p', '--processes', type=int, dest="processes", default=None, help='Number of threads to utilize (Default to the number of installed logical cores - 1)')
    # parser.add_argument('-l', '--load', type=bool, dest="load", default=None, help='Load target dataset (JSON) into database (SQLite)')
    # parser.add_argument('-d', '--dump', type=bool, dest="dump", default=None, help='Dump the target database (SQLite) into a dump file')
    # parser.add_argument('-a', '--validate', type=bool, dest="validate", default=None, help='Validate database content validity')
    # parser.add_argument('-c', '--clean', type=bool, dest="clean", default=None, help='Initialize a clean run (drops previous database tables excluding metadata)')
    # parser.add_argument('-o', '--override', type=bool, dest="override", default=None, help='Override previous data record in the database on conflict')
    
    # args = parser.parse_args()
    
    conn = get_sqlite_conn()                    # GET DB CONNECTION
    drop_all_sqlite_tables(conn)                # CLEAR NON-METADATA TABLES (CLEAN RUN) 
    create_sqlite_db(conn)                      # CREATE NEW DATA TABLE
    
    dataset = load_dataset()                    # LOAD DATASET FROM JSON
    load_to_db(conn, dataset, validate=True)    # INSERT DATA INTO DB + VALIDATION
