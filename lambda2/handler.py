def handler(event, context):
    response = f"Hello! You hit the {event['path']} endpoint in lambda 2"
    return {
        "statusCode": 200,
        "body": response,
        "headers": {"Content-Type": "text/plain"},
    }