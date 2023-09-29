import logging
import os
import mysql.connector
import mysql.connector.types
import pymilvus
from pymilvus import (
    connections,
    utility
)


# logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def connect(alias):
    try:

        logger.info('Connecting to Milvus..\t' + os.getenv('MILVUS_HOST'))
        connections.connect(
            alias=alias,
            host=milvus_host,
            port=milvus_port,
            user=milvus_user,
            password=os.getenv('MILVUS_PASSWORD'),
            db_name=milvus_db_name
        )
        logger.info('SUCCESS, Connected to Milvus.')
    except pymilvus.exceptions.MilvusException as e:
        logger.error("Error connecting to Milvus : " + str(e))
        # raise pymilvus.exceptions.MilvusException
        raise e
    except Exception as e:
        logger.error("Error connecting to Milvus : " + str(e))
        raise e
        # Exception(str(e))


def drop_collection(collection_name, alias):
    try:
        utility.drop_collection(collection_name, using=alias)
    except Exception as e:
        logger.error('ERROR:  Milvus drop collection failed on ', collection_name)
        logger.error(e)
        return False
    return True


def drop_collections(collections_list, alias):
    dropped = []
    not_dropped = []
    for collection in collections_list:
        if drop_collection(collection, alias):
            dropped.append(collection)
        else:
            not_dropped.append(collection)
    return dropped, not_dropped


def history_cleanup():
    # Set up logging
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)s: %(asctime)s: %(message)s')

    # Connect to the database
    try:
        conn = mysql.connector.connect(host=rds_host, user=user_name, passwd=os.getenv('mysql_password'), db=db_name,
                                       port=3306, connect_timeout=5)
    except mysql.connector.Error as e:
        logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
        logger.error("User = " + str(user_name))
        logger.error("Database = " + str(db_name))
        logger.error("Host = " + str(rds_host))
        logger.error(e)
        raise e
        # sys.exit(2)

    logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")
    # TODO: Change it to 14 days after testing on DEV and in PROD
    # for development delete any record older than 7 days
    sql_string = f"select * from tbl_chat_collections where created_at < (CURRENT_DATE() - INTERVAL 7 DAY)"
    collection_names = []
    try:
        mysql_cursor = conn.cursor()

        mysql_cursor.execute(sql_string)

        my_result = mysql_cursor.fetchall()
        # milvus collection drop
        if not connections.has_connection(milvus_alias):
            connect(milvus_alias)

        for record in my_result:
            collection_names.append(record[2])
        dropped_collections, remaining_collection = drop_collections(collection_names, milvus_alias)
        logger.info("Total expired records found:\t"+str(len(my_result)))
        logger.info("Deleted collections from milvus:\t"+str(len(dropped_collections)))

        for sql_record in my_result:
            if sql_record[2] in dropped_collections:
                sql_string = "delete from tbl_chat_collections where id = " + str(sql_record[0])
                mysql_cursor.execute(sql_string)
                conn.commit()
                logger.info("Deleted record id: " + str(sql_record[0]) + " collection: "+ str(sql_record[2]))
            elif sql_record[2] in remaining_collection:
                logger.info("Ignoring deletion from MySQL record for consistency with Milvus.")
                logger.info("id: " + str(sql_record[0]) + " collection: " + str(sql_record[2]))
        logger.info("Deleted records from DB:\t"+str(len(dropped_collections)))
    except mysql.connector.Error as e:
        logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
        logger.error(e)
        raise e
    except Exception as e:
        logger.error("ERROR: Unexpected error while deleting history")
        logger.error(e)
        raise e

    logger.info("Success, deleted records older than 7 days")
    connections.remove_connection(milvus_alias)
    mysql_cursor.close()
    conn.close()


if __name__ == "__main__":
    logger.info("Initializing the ASKREGN History Cleanup script")

    # rds settings - these environment variables are set up in the helm chart
    user_name = os.getenv('mysql_user')
    rds_host = os.getenv('mysql_host')
    db_name = os.getenv('mysql_database')

    # milvus config - these environment variables are set up in the helm chart
    milvus_alias = os.getenv("MILVUS_HISTORY_CONN")
    milvus_host = os.getenv('MILVUS_HOST')
    milvus_port = os.getenv('MILVUS_PORT')
    milvus_user = os.getenv('MILVUS_USER')
    milvus_db_name = os.getenv('MILVUS_DB')

    logger.info("Loaded env variables")
    history_cleanup()
    logger.info("Job Success")