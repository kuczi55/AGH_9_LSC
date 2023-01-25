from parliament import Context, event
from cloudevents.http import CloudEvent
from fer import FER
from io import BytesIO
import os
import boto3
import uuid
import logging
import numpy as np
from PIL import Image
from datetime import datetime

def detect_emotions(context: Context):
    now = datetime.now()
    processing_2_start = f"{now}"
    logging.warning(f"Current Time ={processing_2_start}")
    logging.warning(context.cloud_event)
    logging.warning(os.environ)

    event_data = context.cloud_event.data
    if not event_data:
        return "No data in event"
    bucket_name = event_data.get('bucket')
    if not bucket_name:
        return "No bucket name in event"
    object_key = event_data.get('filename', {})
    if not object_key:
        return "No object key in event"

    if not object_key.endswith(('.jpg', '.jpeg', '.png')):
        return "Object is not image"
    upload_time = event_data.get('upload_time')
    if not upload_time:
        return "No upload time in event"

    processing_1_start = event_data.get('processing_1_start')
    if not processing_1_start:
        return "No processing start time in event"
    
    processing_1_end = event_data.get('processing_1_end')
    if not processing_1_end:
        return "No processing end time in event"

    try:
        s3 = boto3.client('s3')
        s3_response_object = s3.get_object(
            Bucket=bucket_name, Key=object_key)
        object_content = s3_response_object['Body'].read()

        image = Image.open(BytesIO(object_content))
        image = image.convert('RGB')
        # convert image to numpy array
        image = np.array(image)

        print(image)

        emo_detector = FER(mtcnn=True)
        # Capture all the emotions on the image
        captured_emotions = emo_detector.detect_emotions(image)
        # Print all captured emotions with the image
        print(captured_emotions)
        # check if in detections there are at least 1 person

        now = datetime.now()
        processing_2_end = f"{now}"
        output_text = f"Emotions - {object_key}\n"
        output_text += f"Upload time: {upload_time}\n"
        output_text += f"Processing 1 start: {processing_1_start}\n"
        output_text += f"Processing 1 end: {processing_1_end}\n"
        output_text += f"Processing 2 start: {processing_2_start}\n"
        output_text += f"Processing 2 end: {processing_2_end}\n"
        output_text += f"___\n"
        for emotion in captured_emotions:
            # # get key with max value
            max_emotion_key = max(emotion['emotions'].items(),
                                  key=lambda x: x[1])[0]
            output_text += f"Emotion: {str(max_emotion_key)} -  {emotion['emotions'][max_emotion_key]*100}%\n"
            # print(output_text)

        bucket_save_name = 'lsc-test-knative-2-output'
        logging.warning(output_text)
        s3.put_object(Bucket=bucket_save_name, Key=object_key.split('.')[0] + '_out.txt',
                      Body=bytes(output_text, 'utf-8'))
        return "Ok"

    except Exception as e:
        print(e)
        return "Error while processing"



def main(context: Context):
    detection_result = detect_emotions(context)

    if detection_result == "Ok":
        attributes = {
            "type": "lsc-2.success",
            "source": "lsc-2-detection"
        }
        logging.warning("END_OK")
        return CloudEvent(attributes, detection_result)

    attributes = {
        "type": "lsc-2.other",
        "source": "lsc-2-detection"
    }
    logging.warning("END")
    logging.warning(detection_result)
    return CloudEvent(attributes, detection_result)