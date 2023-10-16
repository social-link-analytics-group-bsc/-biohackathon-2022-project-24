# Create empty table
def create_tables(
    conn,
    table_sections,
    table_check,
    table_article_metadata,
    table_journal_metadata,
    table_meshtags,
):
    c = conn.cursor()

    c.execute(
        f"""CREATE TABLE IF NOT EXISTS "{table_sections}" (
	            "pmcid"	TEXT NOT NULL,
	            "intro" TEXT,
                PRIMARY KEY("pmcid")
            )"""
    )
    conn.commit()
    c.execute(
        f"""CREATE TABLE IF NOT EXISTS "{table_article_metadata}" (
                "pmcid"	TEXT,
	            FOREIGN KEY("pmcid") REFERENCES "{table_sections}"("pmcid")
            )"""
    )
    conn.commit()
    c.execute(
        f"""CREATE TABLE IF NOT EXISTS "{table_journal_metadata}" (
                "pmcid"	TEXT,
	            FOREIGN KEY("pmcid") REFERENCES "{table_sections}"("pmcid")
            )"""
    )
    conn.commit()

    c.execute(
        f"""CREATE TABLE IF NOT EXISTS "{table_meshtags}" (
	            "pmcid"	INTEGER NOT NULL,
	            FOREIGN KEY("pmcid") REFERENCES "{table_sections}"("pmcid")
            )"""
    )
    conn.commit()
    c.execute(
        f"""CREATE TABLE IF NOT EXISTS "{table_check}" (
            "pmcid" TEXT NOT NULL,
            FOREIGN KEY("pmcid") REFERENCES "{table_sections}"("pmcid")
            )"""
    )
    conn.commit()


def commit_to_database(conn, pmcid, table, results):
    values_to_record = results
    values_to_record["pmcid"] = pmcid
    sql_query = f"""
    INSERT OR IGNORE INTO {table} ({', '.join([k for k in values_to_record])}) VALUES ({', '.join(['?' for _ in values_to_record])})
    """
    c = conn.cursor()
    c.execute(sql_query, tuple(values_to_record.values()))
    conn.commit()
