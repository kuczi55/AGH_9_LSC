from parliament import Context, event
from cloudevents.http import CloudEvent
from io import BytesIO
import os
import boto3
import uuid
import logging
import numpy as np
from PIL import Image
from imageai.Detection import ObjectDetection
from datetime import datetime


def detect_image(context: Context):
    now = datetime.now()
    processing_1_start = f"{now}"
    logging.warning("Current Time")
    logging.warning(context.cloud_event)
    logging.warning(os.environ)

    event_data = context.cloud_event.data
    if not event_data:
        return "Error", "No data in event"
    
    event_time = event_data.get('eventTime')
    if not event_time:
        return "Error", "No eventTime in event"
    s3_data = event_data.get('s3')
    if not s3_data:
        return "Error", "No s3 data in event"
    bucket_name = s3_data.get('bucket', {}).get('name')
    if not bucket_name:
        return "Error", "No bucket name in event"
    object_key = s3_data.get('object', {}).get('key')
    if not object_key:
        return "Error", "No object key in event"

    # check if object is image
    if not object_key.endswith(('.jpg', '.jpeg', '.png')):
        return "Error", "Object is not image"

    try:
        s3 = boto3.client('s3')
        s3_response_object = s3.get_object(
            Bucket=bucket_name, Key=object_key)
        object_content = s3_response_object['Body'].read()

        image = Image.open(BytesIO(object_content))
        image = image.convert('RGB')

        print(image)

        detector = ObjectDetection()
        detector.setModelTypeAsRetinaNet()
        # load model from current folder from model.pth file

        execution_path = os.getcwd()
        detector.setModelPath(os.path.join(
            execution_path, "model.pth"))
        detector.loadModel()
        # convert image to numpy array

        # detectObjectsFromImage from object_content stream
        detections = detector.detectObjectsFromImage(
            input_image=image, minimum_percentage_probability=30)

        # check if in detections there are at least 1 person


        now = datetime.now()
        processing_1_end = f"{now}"

        def contains_person(detections):
            for eachObject in detections:
                if eachObject["name"] == "person":
                    return True
            return False

        if contains_person(detections):
            return "Detection", {
                "bucket": bucket_name,
                "filename": object_key,
                "upload_time": event_time,
                "processing_1_start": processing_1_start,
                "processing_1_end": processing_1_end
            }
        return "No detection", "No person"

    except Exception as e:
        print(e)
        return "Error", "Error while processing"



def main(context: Context):
    status, detection_result = detect_image(context)

    if status == "Detection":
        attributes = {
            "type": "lsc-1.success",
            "source": "lsc-1-detection"
        }
        logging.warning("END_SUCCESS")
        return CloudEvent(attributes, detection_result)

    attributes = {
        "type": "lsc-1.other",
        "source": "lsc-1-detection"
    }
    logging.warning("END")
    logging.warning(detection_result)
    return CloudEvent(attributes, detection_result)