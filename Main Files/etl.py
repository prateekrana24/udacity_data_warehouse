import configparser
import psycopg2
from sql_queries import copy_table_queries, insert_table_queries


def load_staging_tables(cur, conn):
    print("loading the staging tables!")
    for query in copy_table_queries:
        cur.execute(query)
        conn.commit()
    print("done loading the staging tables!")

def insert_tables(cur, conn):
    print("inserting the tables!")
    for query in insert_table_queries:
        cur.execute(query)
        conn.commit()
    print("finished inserting the tables!")

def main():
    config = configparser.ConfigParser()
    config.read('dwh.cfg')

    conn = psycopg2.connect("host={} dbname={} user={} password={} port={}".format(*config['CLUSTER'].values()))
    cur = conn.cursor()
    
    load_staging_tables(cur, conn)
    insert_tables(cur, conn)

    conn.close()


if __name__ == "__main__":
    main()