OPEN_API_KEYS = {
    "OPENAI_API_BASE": "val1","OPENAI_API_KEY": "val2","OPENAI_API_TYPE": "val2","OPENAI_API_VERSION": "val3",
}

import json


def lambda_handler(event, context):
    msg = json.dumps(event)
    # msg = "HELLO WORLD!"
    path = event["routeKey"] if "routeKey" in event else "EMPTY"
    print(path)
    if path == "/api-key":
        msg = "You've hit the Api-key route!"
    # get_secret()
    # return {"statusCode": 200, "body": msg + "\n" + json.dumps(event) + "\n" + path}
    return {"statusCode": 200, "body": OPEN_API_KEYS}
    # return {
    #     "statusCode": 200,
    #     "body": {"keys": OPEN_API_KEYS, "message": f"{msg}", "api_path": f"{path}"},
    # }
    # return {
    #     "statusCode": 200,
    #     "body": {
    # "OPENAI_API_BASE": "val1",
    # "OPENAI_API_KEY": "val2",
    # "OPENAI_API_TYPE": "val2",
    # "OPENAI_API_VERSION": "val3",
    #     },
    # }


# sam local invoke -e .\events\eventTest.json
