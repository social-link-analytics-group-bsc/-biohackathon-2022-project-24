import sqlite3
import os
import yaml


config_path = os.path.join(os.path.dirname(
    __file__), '../config', 'config.yaml')
config_all = yaml.safe_load(open(config_path))

# Global client
global _sql_conn
_sql_conn = None


def commitToDatabase(pmcid, dictSection, dictMetadata, supMaterial):
    c = get_connector()
    c.execute(f'''INSERT OR IGNORE INTO Main
    values ("{pmcid}", "{dictSection["Intro"]}", "{dictSection["Method"]}",
    "{dictSection["Result"]}", "{dictSection["Discussion"]}", "{supMaterial}",
     "{dictMetadata["issn"]["ppub"]}", "{dictMetadata["issn"]["epub"]}",
     "{dictMetadata["journalTitle"]}", "{dictMetadata["publisherName"]}")''')
    _sql_conn.commit()
    print(f"Inserted {pmcid}")
    c.close()


def drop_database():
    c = get_connector()
    c.execute('''DROP TABLE IF EXISTS Main''')
    c.close()


def create_database():
    c = get_connector()
    c.execute('''CREATE TABLE IF NOT EXISTS "Main" (
        "pmcid"	TEXT NOT NULL,
        "Introduction"	TEXT,
        "Methods" TEXT,
        "Result" TEXT,
        "Discussion" TEXT,
        "SupMaterial" TEXT,
        "ISSN PPUB" TEXT,
        "ISSN EPUB" TEXT,
        "JournalTitle" TEXT,
        "PublisherName" TEXT,
        PRIMARY KEY("pmcid")
            )''')
    c.close()


def _data_retrieve(command):
    c = get_connector()
    c.execute(command)
    for row in c.fetchall():
        yield dict(row)
    c.close()


def retrieve_existing_record():

    command = """SELECT pmcid FROM MAIN;"""
    return _data_retrieve(command)


def retrieve_method_section():
    command = """SELECT pmcid, Methods FROM MAIN;"""
    return _data_retrieve(command)


def get_connector():
    global _sql_conn
    try:
        return _sql_conn.cursor()
    except Exception as ex:
        db_file = config_all['sql_params']['db_file']

        # # Connect to the SQLite database
        # # If name not found, it will create a new database
        _sql_conn = sqlite3.connect(db_file)
        # To return dictionary
        _sql_conn.row_factory = sqlite3.Row
    return _sql_conn.cursor()
