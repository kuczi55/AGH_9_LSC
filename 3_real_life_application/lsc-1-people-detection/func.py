from parliament import Context, event
from cloudevents.http import CloudEvent
from io import BytesIO
import os
import boto3
import uuid
import numpy as np
from PIL import Image
from imageai.Detection import ObjectDetection

def detect_image(context: Context):
    event_attr = context['cloud_event']['attributes']
    if not event_attr:
        return "No attributes in event"
    event_data = context['cloud_event']['data']
    if not event_data:
        return "No data in event"
    s3_data = event_data.get('s3')
    if not s3_data:
        return "No s3 data in event"
    bucket_name = s3_data.get('bucket', {}).get('name')
    if not bucket_name:
        return "No bucket name in event"
    object_key = s3_data.get('object', {}).get('key')
    if not object_key:
        return "No object key in event"

    # check if object is image
    if not object_key.endswith(('.jpg', '.jpeg', '.png')):
        return "Object is not image"

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
        detector.setModelPath(os.path.join(
            execution_path, "retinanet_resnet50_fpn_coco-eeacb38b.pth"))
        detector.loadModel()
        # convert image to numpy array

        # detectObjectsFromImage from object_content stream
        detections = detector.detectObjectsFromImage(
            input_image=image, minimum_percentage_probability=30)

        # check if in detections there are at least 1 person

        def contains_person(detections):
            for eachObject in detections:
                if eachObject["name"] == "person":
                    return True
            return False

        if contains_person(detections):
            return "Person"
        return "No person"

    except Exception as e:
        print(e)
        return "Error while processing"



def main(context: Context):
    detection_result = detect_image(context)

    if detection_result == "Person":
        attributes = {
            "type": "lsc-1.success",
            "source": "lsc-1-detection"
        }
        return CloudEvent(attributes, detection_result)

    attributes = {
        "type": "lsc-1.other",
        "source": "lsc-1-detection"
    }
    return CloudEvent(attributes, detection_result)