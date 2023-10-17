import json


# Create empty table
def create_tables(
    conn,
    table_sections,
    table_status,
    table_metadata,
):
    c = conn.cursor()

    c.execute(
        f"""CREATE TABLE IF NOT EXISTS "{table_sections}" (
	            "pmcid"	TEXT NOT NULL,
                PRIMARY KEY("pmcid")
            )"""
    )
    conn.commit()
    c.execute(
        f"""CREATE TABLE IF NOT EXISTS "{table_metadata}" (
                "pmcid"	TEXT,
	            FOREIGN KEY("pmcid") REFERENCES "{table_sections}"("pmcid")
            )"""
    )
    conn.commit()
    c.execute(
        f"""CREATE TABLE IF NOT EXISTS "{table_status}" (
            "pmcid" TEXT NOT NULL,
            FOREIGN KEY("pmcid") REFERENCES "{table_sections}"("pmcid")
            )"""
    )
    conn.commit()


def ensure_column_exists(conn, table, column_name):
    c = conn.cursor()
    c.execute(f"PRAGMA table_info({table})")
    existing_columns = [column[1] for column in c.fetchall()]

    if column_name not in existing_columns:
        c.execute(f"ALTER TABLE {table} ADD COLUMN {column_name} TEXT")
        conn.commit()


def flatten_dict(d, parent_key="", sep="_"):
    return_dict = {}
    for k in d:
        if parent_key:
            new_key = f"{parent_key}{sep}{k}"
        else:
            new_key = k
        if isinstance(d[k], dict):
            return_dict.update(flatten_dict(d[k], new_key, sep=sep))
        else:
            return_dict[k] = d[k]
    return return_dict


def commit_to_database(conn, pmcid, table, results):
    # Ensure all the dict are flatten to work with SQL
    results = flatten_dict(results)
    results["pmcid"] = pmcid
    # Ensure the table has the necessary columns
    for key in results:
        # Check if it is a list:
        if isinstance(results[key], list):
            results[key] = json.dumps(results[key])
        ensure_column_exists(conn, table, key)
    sql_query = f"""
    INSERT OR IGNORE INTO {table} ({', '.join([k for k in results])}) VALUES ({', '.join(['?' for _ in results])})
    """
    c = conn.cursor()
    c.execute(sql_query, tuple(results.values()))
    conn.commit()
