from parliament import Context, event
import logging
import requests
import json
import os


# @event(event_source="aws:s3")
@event
def main(context: Context):
    """
    Function template
    The context parameter contains the Flask request object and any
    CloudEvent received with the request.
    """

    # Add your business logic here

    # The return value here will be applied as the data attribute
    # of a CloudEvent returned to the function invoker
    print("print")
    logging.warning(f'{os.environ["EXAMPLE1"]}, {os.environ["ACCESSKEY"]},  {os.environ["SECRET"]}')
    logging.warning(context.request)
    logging.warning(context.cloud_event)
    data=json.dumps(context.cloud_event.data)
    requests.post("https://webhook.site/4e5ae92d-8d5f-44a4-bdac-58cb7e1ffb5f", json=data)
    # context to JSON


    print(context.cloud_event.data)

    return context.cloud_event.data