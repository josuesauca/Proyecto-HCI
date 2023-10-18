from django.shortcuts import render
import requests, uuid, json
from django.http import HttpResponse

# Create your views here.

def Inicio(request):

    endpoint = 'https://api.cognitive.microsofttranslator.com/'
    key = 'fa12509d93ab47b691fff1f111a50c7f'
    location = 'eastus'

    path = '/translate'
    constructed_url = endpoint + path
    params = {
        'api-version': '3.0',
        'from': 'en',
        'to': ['es', 'it']
    }

    headers = {
        'Ocp-Apim-Subscription-Key': key,
        # location required if you're using a multi-service or regional (not global) resource.
        'Ocp-Apim-Subscription-Region': location,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }

    # You can pass more than one object in body.
    body = [{
        'text': 'Hello, friend! What did you do today?'
    }]

    request = requests.post(constructed_url, params=params, headers=headers, json=body)
    response = request.json()

    print(json.dumps(response, sort_keys=True, ensure_ascii=False, indent=4, separators=(',', ': ')))

    msg = f'hola si salio'

    return HttpResponse(msg, content_type='text/plain')



from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials

from array import array
import os
from PIL import Image
import sys
import time

def leer_imagenes(reques):

    endpoint = 'https://saucajosue.cognitiveservices.azure.com/'
    key = '59fdd9553b4643f29bb2bbb0802aad32'

    read_image_url = "https://s.bibliaon.com/es/imagenes/gracias-senor-por-este-nuevo-dia-que-me-permites-comenzar-0.jpg"

    computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(key))

    print("===== Read File - remote =====")

    read_response = computervision_client.read(read_image_url,  raw=True)

    read_operation_location = read_response.headers["Operation-Location"]
    operation_id = read_operation_location.split("/")[-1]

    # Call the "GET" API and wait for it to retrieve the results 
    while True:
        read_result = computervision_client.get_read_result(operation_id)
        if read_result.status not in ['notStarted', 'running']:
            break
        time.sleep(1)

    # Print the detected text, line by line
    if read_result.status == OperationStatusCodes.succeeded:
        for text_result in read_result.analyze_result.read_results:
            for line in text_result.lines:
                print(line.text)
                #print(line.bounding_box)
    print()
    '''
    END - Read File - remote
    '''

    print("End of Computer Vision quickstart.")

    msg = f'leyo imagenes' 

    return HttpResponse(msg, content_type='text/plain')