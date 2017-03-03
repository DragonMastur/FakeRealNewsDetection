import json

def analyze(event, context):
    result = {
        "news-url": None,
        "news-type": "FIND"
    }
    response = {
        "statusCode": 200,
        "result": json.dumps(result)
    }
    return response

def hello(event, context):
    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response

    # Use this code if you don't use the http event with the LAMBDA-PROXY integration
    """
    return {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "event": event
    }
    """
