"""External Libraries"""
import mysql.connector

# from flask import jsonify
import json
import logging
from retry import retry

# TODO : Umar please pick the sql credentials from the aws
MySQL_CONFIG = {
    "host": os.getenv("mysql_host"),
    "user": os.getenv("mysql_user"),
    "password": os.getenv("mysql_password"),
    "database": os.getenv("mysql_database"),
}


class MySqlDBHelper:
    """
    This is a wrapper class used for connecting to MySQL Database.
    """

    # Singleton object creation
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    # Constructor
    def __init__(self):
        logging.info("Class MySqlHelper()")
        self._connection = None
        self.__connect()

    # Method used to connect to DB
    @retry(
        exceptions=mysql.connector.Error,
        tries=3,
        delay=5,
        max_delay=20,
        backoff=2,
        jitter=(1, 3),
    )
    def __connect(self):
        """
        Arguments : None
        Return Type : None
        """
        try:
            logging.info("Creating a new connection to the sql database..!")

            self._connection = mysql.connector.connect(**MySQL_CONFIG)
            # print('Connected to the sql database successfully!')

            # Creating the feedback table if it doesn't exist
            create_feedback_query = """
                        CREATE TABLE IF NOT EXISTS feedback (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            userId VARCHAR(255) NOT NULL,
                            name VARCHAR(255) NOT NULL,
                            comments VARCHAR(255) NOT NULL,
                            rating FLOAT NOT NULL,
                            isResolved BIT DEFAULT 0,
                            createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
            """

            Auth_type_query = """
                CREATE TABLE IF NOT EXISTS AuthType (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(255) NOT NULL UNIQUE,
                        isActive BIT DEFAULT 1,
                        createdOn TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """

            admin_access_query = """
                CREATE TABLE IF NOT EXISTS AuthControl (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        userID VARCHAR(255) NOT NULL UNIQUE,
                        authType INT NOT NULL,
                        isActive BIT DEFAULT 1,
                        createdOn TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        CONSTRAINT FK_AuthType_Access FOREIGN KEY
                        (authType) REFERENCES AuthType(id)
                )
            """
            chat_collections_query = """
                CREATE TABLE IF NOT EXISTS `tbl_chat_collections` (
                    `id` int NOT NULL AUTO_INCREMENT,
                    `user_id` varchar(100) NOT NULL,
                    `collection_name` varchar(100) NOT NULL,
                    `chat_initial_text` varchar(100)  DEFAULT NULL,
                    `chat_count` int NOT NULL,
                    `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    `last_updated` timestamp NOT NULL ON UPDATE CURRENT_TIMESTAMP,
                    PRIMARY KEY (`id`),
                    UNIQUE (`collection_name`)
                    ) ;
            """

            cursor = self._connection.cursor()

            cursor.execute(create_feedback_query)
            cursor.execute(Auth_type_query)
            cursor.execute(admin_access_query)
            cursor.execute(chat_collections_query)

            self._connection.commit()
            cursor.close()
            logging.info("Connected to the sql database successfully!")
        except mysql.connector.Error as e:
            logging.error(f"Error Connecting to the sql database :  {str(e)}")
            raise e
        except Exception as e:
            logging.error(f"Error Connecting to the sql database :  {str(e)}")

    def __reconnect(self, attempts=3, delay=5):
        """
        To reconnect to SQL server.
        Arguments : None
        Return Bool : True if connection established successfully, False otherwise
        """
        try:
            if self._connection is not None:
                self._connection.reconnect(attempts=attempts, delay=delay)
                logging.info("Reconnected to the sql database successfully!")
            else:
                self.__connect()  # This will set self._connection variable
        except Exception as e:
            logging.error(f"Error reconnecting to the sql database :  {str(e)}")

    def get_connection(self):
        if self._connection:
            if self._connection.is_connected():
                return self._connection
        self.__reconnect()
        return self._connection

    # Method used to execute query
    def save_data(self, query, data):
        """
        Arguments :
            query : SQL query to be executed
            data : Data to be inserted into the database
        Return Type : Success / Failed boolean value
        """
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            cursor.execute(query, data)
            connection.commit()
            cursor.close()
            logging.info("Successfully executed the query, save_data()")
            return True

        except Exception as e:
            logging.error(f"Error in save_data():  {str(e)}")
            return False

    # Method used to get the data
    def get_data(self, query, data):
        """
        Arguments :
            query : SQL query to be executed
            data : Data to be append to the query

        Return Type : List of data
        """
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            cursor.execute(query, data)

            columns = [column[0] for column in cursor.description]
            result_set = cursor.fetchall()

            data = []
            for row in result_set:
                row_dict = {}
                for i, value in enumerate(row):
                    # formatting boolean value
                    column_name = columns[i]
                    converted_value = (
                        bool(value)
                        if column_name == "isResolved" or column_name == "isActive"
                        else value
                    )
                    converted_value = (
                        converted_value.decode("utf-8")
                        if type(converted_value) == bytes
                        else converted_value
                    )
                    row_dict[columns[i]] = converted_value
                data.append(row_dict)

            cursor.close()

            # Serializing the data
            # print(data)
            serialized_data = json.loads(json.dumps(data, default=str))
            logging.info("Successfully fetched data from MySQL DB")
            # return jsonify(serialized_data)
            return json.dumps(serialized_data)

        except Exception as e:
            logging.error(f"Error fetching data from the database:  {str(e)}")

    # TODO : Main method to insert the method to chat meta data
    def insert_collection_data(self, data):
        """
        Arguments :
            data : Data to be append to the query

        Return Type : Success / Failed boolean value
        """

        query = f"""
            INSERT INTO `tbl_chat_collections`
            (
            `user_id`,
            `collection_name`,
            `chat_initial_text`,
            `chat_count`
            )
            VALUES (%s, %s, %s, %s)

            ;

        """

        return self.save_data(query, data)

    # TODO : Subsequent method to keep updating the meta data
    def update_collection_data(self, collection_name, chat_text):
        """
        Arguments :
            collection_name : collection name of the chat to be set
            chat_text : initial text of the chat response

        Return Type : Success / Failed boolean value
        """

        try:
            query = """
            UPDATE `tbl_chat_collections`
            SET
            chat_initial_text = %s,
            chat_count = chat_count + 1
            WHERE
            collection_name = %s
        """

            values = (
                chat_text,
                collection_name,
            )
            logging.info("Successfully updated data from MySQL DB")
            return self.save_data(query, values)

        except Exception as e:
            logging.error(f"Error updating the MySQL DB:  {str(e)}")
            return False

    # TODO : Method to get the meta data chats from sql
    def get_chats(self, mail_id):
        """
        Arguments :
            mail_id : mail_id to get chats against

        Return Type : List of data
        """

        query = f"""
            SELECT * FROM `tbl_chat_collections`
            WHERE `user_id` = %s and chat_count > 0

        """
        data = (mail_id,)
        return self.get_data(query, data)
