from io import BytesIO
from fer import FER
import os
import boto3
import uuid
import numpy as np
from PIL import Image
from imageai.Detection import ObjectDetection
import datetime


def main(context):

    # JUST FOR DEBUGGING
    os.environ['AWS_ACCESS_KEY_ID'] = '<access_key>'
    os.environ['AWS_SECRET_ACCESS_KEY'] = '<secret_key>'
    # ---
    execution_path = os.getcwd()

    event_data = context['cloud_event']['data']
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

    processing_start = event_data.get('processing_start')
    if not processing_start:
        return "No processing start time in event"

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

        output_text = f"Emotions - {object_key}\n"
        output_text += f"Date: {upload_time}\n"
        output_text += f"Processing start: {processing_start}\n"
        output_text += f"___"
        now = datetime.datetime.now()

        output_text += f"Processing finished: {now}\n"
        for emotion in captured_emotions:
            print(emotion)
            # # get key with max value
            max_emotion_key = max(emotion['emotions'].items(),
                                  key=lambda x: x[1])[0]
            output_text += f"Emotion: {str(max_emotion_key)} -  {emotion['emotions'][max_emotion_key]*100}%\n"
            # print(output_text)

        bucket_save_name = 'lsc-test-knative-2-output'
        print(output_text)
        s3.put_object(Bucket=bucket_save_name, Key=object_key.split('.')[0] + '_out.txt',
                      Body=bytes(output_text, 'utf-8'))

    except Exception as e:
        print(e)
        return "Error while processing"


# EXAMPLE CONTEXT                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                # 'h1JmajPSH7GnTLweyr4HNXecwKTalnkevABugGpF84A06W7SZxbIrLt3R2mLNIkXM4/CAXS41tiEvv/wVUNiDyalgWxdPz6q', 'x-amz-request-id': 'PNYC54YH8CBSP8B5'}, 's3': {'bucket': {'arn': 'arn:aws:s3:::lsc-test-knative-2', 'name': 'lsc-test-knative-2', 'ownerIdentity': {'principalId': 'A1U2OQHCKCVL4N'}}, 'configurationId': 'io.triggermesh.awss3sources.default.lsc-awss3-source', 'object': {'key': 'Screenshot_Code_2023-01-08_162341.png', 'sequencer': '0063BAE05C9E4D0A57'}, 's3SchemaVersion': '1.0'}, 'userIdentity': {'principalId': 'AWS:AIDARLUNRS7SG3R3M3DPK'}}}
content = {
    "cloud_event": {
        "attributes": {
            "specversion": "1.0",
            "id": "cf222dc4-fb6d-44fd-ad13-646e67157810",
            "source": "/parliament/function",
            "type": "parliament.response",
            "datacontenttype": "text/html; charset=utf-8",
            "time": "2023-01-08T15:25:54.344933Z",
            "knativearrivaltime": "2023-01-08T15:25:54.348380645Z"
        },
        "data": {
            "bucket": "lsc-test-knative-2",
            "filename": "Screenshot_Firefox_2023-01-08_174601.png",
            "upload_time": "2023-01-08T15:25:16.639Z",
            "processing_start": "2023-01-08T15:25:54.344Z",
        }
    }
}

main(content)
