# import json
# from helper.sql_helper import MySqlDBHelper
# from api.eula import Eula


def lambda_handler(event, context):
    # db_helper = MySqlDBHelper()
    # eula = Eula(db_helper, app)
    # msg = eula.is_eula_consented(user_email)
    return {"statusCode": 200, "body": "Hi Umar"}


# sam local invoke -e .\events\eventTest.json
