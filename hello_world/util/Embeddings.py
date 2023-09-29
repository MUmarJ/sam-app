import openai
import os
from retry import retry
import logging
from config import Config

logging.info(os.getenv("OPENAI_API_KEY"))

openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_type = os.getenv("OPENAI_API_TYPE")
openai.api_base = os.getenv("OPENAI_API_BASE")
openai.api_version = os.getenv("OPENAI_API_VERSION")


@retry(exceptions=Exception, tries=3, delay=5)
def get_embeddings(text):
    try:
        hash_string = "#"*100
        logging.info(f"/get_embeddings : Getting embeddings for {hash_string}...")
        logging.info(f"/get/embeddings:  {openai}")
        logging.info(openai.Embedding.create)
        embeddings = openai.Embedding.create(
            model="text-embedding-ada-002",
            engine='REGNADAV2',
            input=text.replace("\n", " "),
            request_timeout=Config.REQUEST_TIMEOUT
            )
        logging.info(f"/get_embeddings : Fetched embeddings for {hash_string}...")

        vector = embeddings['data'][0]['embedding'] 
        # logging.info(f"/get_embeddings : Vector data : {vector} ")

        return vector
    
    except Exception as e:
        logging.error("Unable to fetch embeddings  " + str(e))
        raise Exception(str(e))
