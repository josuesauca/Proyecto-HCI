from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group

from django.conf import settings



from .decorators import unauthenticated_user,admin_only
from .models import *
from .forms import FormularioTraduccion,FormularioTraduccionObtenida


#librerias para leer texto de imagenes
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials


from array import array
import os
from PIL import Image
import sys
import time

import requests, uuid, json

# Create your views here.

def PaginaInicio(request):

    


    return render(request, 'index.html', {})

class AccionesUsuario(HttpRequest):

    @unauthenticated_user
    def log_in(request):
        if(request.method == "POST"):
            user = authenticate(request, username=request.POST["username"], password=request.POST["password"])
            if user is None:
                messages.error(request,"Usuario no encontrado")
                return redirect("login")
            else:
                login(request, user)
                return redirect("index")
        else:
            return render(request, "Usuario/Login.html",{})
            
    def log_out(request):
        logout(request)
        return redirect("index")
    
    def registro_usuario(request):
        if(request.method == "POST"):
            if request.POST["password1"] == request.POST["password2"]:
                username = request.POST['username']
                email = request.POST['email']
                password1 = request.POST['password1']
                user = User.objects.create_user(
                        username=username, password=password1, email=email)
                
                my_group = Group.objects.get(name='usuario') 
                my_group.user_set.add(user)

            user.save()
            return redirect("login")
        else:
            return render(request, "Usuario/Usuario.html",{})
    
    def traducir_texto(request):

        endpoint = 'https://saucajosue.cognitiveservices.azure.com/'
        key = '59fdd9553b4643f29bb2bbb0802aad32'

        #imagenTraduccion = Traduccion.objects.first().imagenTraduccion.url
        
        read_image_url = "https://s.bibliaon.com/es/imagenes/gracias-senor-por-este-nuevo-dia-que-me-permites-comenzar-0.jpg"

        #read_image_url = 'https://images.vexels.com/content/222142/preview/graffiti-alphabet-letter-set-da9351.png'

        image_path = os.path.join(settings.MEDIA_ROOT, '1.png')

        with open(image_path, 'rb') as f:
            image_data = f.read()


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

        palabras_imagen = ""
        if read_result.status == OperationStatusCodes.succeeded:
            for text_result in read_result.analyze_result.read_results:
                for line in text_result.lines:
                    #print(line.text)
                    palabras_imagen = palabras_imagen + " " + line.text
        print("palabras obtenidas ", palabras_imagen)


        #Traduccir el texto obtenido

        endpoint = 'https://api.cognitive.microsofttranslator.com/'
        key = 'fa12509d93ab47b691fff1f111a50c7f'
        location = 'eastus'

        path = '/translate'
        constructed_url = endpoint + path
        params = {
            'api-version': '3.0',
            'from': 'es',
            'to': ['en','it']
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
            'text': palabras_imagen
        }]

        request = requests.post(constructed_url, params=params, headers=headers, json=body)
        response = request.json()

        print(json.dumps(response, sort_keys=True, ensure_ascii=False, indent=4, separators=(',', ': ')))

        return redirect("index")


"""
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
"""

"""

def leer_imagenes(reques):



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
"""