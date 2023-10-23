from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group

from django.conf import settings


from .decorators import unauthenticated_user,admin_only
from .models import *
from .forms import *


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

#Libreria del firebase
import pyrebase

# Create your views here.

def guardarImagen(request):
    formulario = FormularioImagen()
    if request.method == 'POST':
        #imagen = request.POST.get('input').name
        #print("url",request.FILES['input'].temporary_file_path())
        #print("url",imagen)
        formulario = FormularioImagen(request.POST,request.FILES)
        #AccionesUsuario.guardar_imagen(request.FILES.get('imagenTraduccion'))

        if formulario.is_valid():
            #print('entra aqui',request.FILES)
            #formulario.save()
            AccionesUsuario.guardar_imagen(str(request.FILES.get('imagenTraduccion')))

        return render(request, "Traducciones/IngresarTraducciones.html",{'form':formulario})
    else:
        return render(request, "Traducciones/IngresarTraducciones.html",{'form':formulario})

def PaginaInicio(request):

    AccionesUsuario.obtener_imagen()

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
        
    def guardar_imagen(url):
        firebaseConfig = {
            "apiKey": "AIzaSyD8kAB8294CT7IZRZ8lV_Pc6EIZhOP0yJ0",
            "authDomain": "trabajo-autonomo-3-283ba.firebaseapp.com",
            "projectId": "trabajo-autonomo-3-283ba",
            "storageBucket": "trabajo-autonomo-3-283ba.appspot.com",
            "messagingSenderId": "158058285647",
            "appId": "1:158058285647:web:ab8a77af641bd438f7f83a",
            'serviceAccount' : {
                                    "type": "service_account",
                                    "project_id": "trabajo-autonomo-3-283ba",
                                    "private_key_id": "0da389d4bf98c1de7c54bc49df9520bbc178b209",
                                    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDARGIM8GJgDlV8\nCe5SR/tNTx9TLdG3lVHWzTexehYQIKL+CqkkL/tiRwbR4aQSNhcvKJNWDfKN5MVK\nRojFkR77Y6LcPqrOORXI4/9Mkb9OREZ6Sxkf6K6xxfaMeuj7SCwz0J0U6fwHHx0L\nI2BrZzab0wVtrInoGiFh2tpr8DXVZ2sv5Iq0PF610ox4VCpIoRw2Fqba3ThP9D2h\nh1B0n25Deze7cLnSIOMnA3JZCS101y9UvfMX6lgT25kH0V6x5ZRj1lpJMQBBmWd5\nHJVmHE+ZNOd90/ncXkbndtzvUIIm+tV6iu7ntR07Sq9D3wY/vICj8agfYSkNsWg8\npS2GZEr/AgMBAAECggEAOuK2xQ+6kYDSXbMM8tZo+TyKc4dM+9UXw5oGvKyPpVDZ\nmsTZGOQ5MdhfFljtT0aRwzfCKFENQLgYVK9VpGzV+FiDwMDQv2hsa6KoxmK9HNN8\nYmgtwcAaAQiIgm4CfTOVlikGcylWrzewRYEIPtzVtNPkjbqSYivenYHR880WL818\nYEhleRLmspoMNsDQn0ROIPfJ0j+LekwOE4QwZkSf/2Kj08LE8tVaLnQiTNFjGojb\ng0JuK67ln+ZFVFh4DqbVqmyS90/Z/T0mH+O8mbFVGNPpfAMSkiq3TKfuLuT3ULXi\naCJ19JlcnSka3bMHEl00tPul8mTov7eGrQmpvesbAQKBgQDzn1ibHf4QZJlDY7P7\nr/5A7erBIBcakl+vSaIBA7MubK08U37lBaAnfR7jr0cEszRqN23rb9rsFI4+e0PF\nkB2lbGmD+QoyFWcxvSY5H8RVEwCtEi3UDjwNe0PQDKe5ERiEFS8NqY5+9FZTYk2G\nAex9ec0kiyAqrjbZrOy2djMiDwKBgQDKCRagfiiti63SaAY5AKWK6jnXHOlyz/O/\nbTESFo9R2QQEth6dUtm+XrdY4TeZjfTuYp55jIx/S/smlL5qaYYrWpKFP+R3r6AO\nYyuQcj58YmCvWdZTPrXYzkM8wPLIMmMLHuTvIZclFMiWKDOsC/dOifJg6biJLjGF\noFj6Ynh4EQKBgQCFXOGAaLa/+pH71gSc7wbcPGGaPxrmrOI8bq6Ep6Xa8BsVPw/k\nB2RYuaHDOhxCcmdrDdTaYW0Sd142zfuXlwDjoalRWW8/Y4AONmFKPB2aBMEF/UGh\nJ/mv156TsZnPMZCeHYqYjA05akAnfVS62yq+tYKbUp3VP3E/T+51I9dx+QKBgHoc\nkiOA/R8frHjezNwJKwVSWpFM9UCiteV+nska/5btvwMF/G0EVX09jD3ZKhzSczbe\nPoCi1YxfJTaFcq2oiCKOBL8rBfDdIrVvdTZCBshxQZTajLMV1R1sVbFTwaoE4l4n\nVyG9wLf13uL6+3hCZ0B+GhQ/T30CgYYNi5oSiFOxAoGBAMT7ZJlyG0HUDDkr23BF\nBNR+Q+6VOY3SeCB45CNkqWMwk/HngMjQwDjZsmyCIDIqkfRrH70D9iEFqTX+y7Rt\nW/SmTZMZ9ZjL/Ir/Yqz9cgnXAEccYdbhtZlveZQW+lRq1pUVTNmH4JZ4+E73NaMy\nUh/u1QFV1pxtRt6U3j9lYq6P\n-----END PRIVATE KEY-----\n",
                                    "client_email": "firebase-adminsdk-ks91j@trabajo-autonomo-3-283ba.iam.gserviceaccount.com",
                                    "client_id": "117284635281132318881",
                                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                                    "token_uri": "https://oauth2.googleapis.com/token",
                                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                                    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-ks91j%40trabajo-autonomo-3-283ba.iam.gserviceaccount.com",
                                    "universe_domain": "googleapis.com"
                                },
            "databaseURL" : "https://trabajo-autonomo-3-283ba-default-rtdb.firebaseio.com/"
        }

        path_imagen = str(url)
        image_name = path_imagen.split('/')[-1]

        print(image_name,"hola")

        firebase = pyrebase.initialize_app(firebaseConfig)
        storage = firebase.storage()
        image_path = os.path.join(settings.MEDIA_ROOT,image_name)
        
        print(image_path,"path")
        storage.child(url).put(image_path)

    def obtener_imagen():
        firebaseConfig = {
            "apiKey": "AIzaSyD8kAB8294CT7IZRZ8lV_Pc6EIZhOP0yJ0",
            "authDomain": "trabajo-autonomo-3-283ba.firebaseapp.com",
            "projectId": "trabajo-autonomo-3-283ba",
            "storageBucket": "trabajo-autonomo-3-283ba.appspot.com",
            "messagingSenderId": "158058285647",
            "appId": "1:158058285647:web:ab8a77af641bd438f7f83a",
            'serviceAccount' : {
                                    "type": "service_account",
                                    "project_id": "trabajo-autonomo-3-283ba",
                                    "private_key_id": "0da389d4bf98c1de7c54bc49df9520bbc178b209",
                                    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDARGIM8GJgDlV8\nCe5SR/tNTx9TLdG3lVHWzTexehYQIKL+CqkkL/tiRwbR4aQSNhcvKJNWDfKN5MVK\nRojFkR77Y6LcPqrOORXI4/9Mkb9OREZ6Sxkf6K6xxfaMeuj7SCwz0J0U6fwHHx0L\nI2BrZzab0wVtrInoGiFh2tpr8DXVZ2sv5Iq0PF610ox4VCpIoRw2Fqba3ThP9D2h\nh1B0n25Deze7cLnSIOMnA3JZCS101y9UvfMX6lgT25kH0V6x5ZRj1lpJMQBBmWd5\nHJVmHE+ZNOd90/ncXkbndtzvUIIm+tV6iu7ntR07Sq9D3wY/vICj8agfYSkNsWg8\npS2GZEr/AgMBAAECggEAOuK2xQ+6kYDSXbMM8tZo+TyKc4dM+9UXw5oGvKyPpVDZ\nmsTZGOQ5MdhfFljtT0aRwzfCKFENQLgYVK9VpGzV+FiDwMDQv2hsa6KoxmK9HNN8\nYmgtwcAaAQiIgm4CfTOVlikGcylWrzewRYEIPtzVtNPkjbqSYivenYHR880WL818\nYEhleRLmspoMNsDQn0ROIPfJ0j+LekwOE4QwZkSf/2Kj08LE8tVaLnQiTNFjGojb\ng0JuK67ln+ZFVFh4DqbVqmyS90/Z/T0mH+O8mbFVGNPpfAMSkiq3TKfuLuT3ULXi\naCJ19JlcnSka3bMHEl00tPul8mTov7eGrQmpvesbAQKBgQDzn1ibHf4QZJlDY7P7\nr/5A7erBIBcakl+vSaIBA7MubK08U37lBaAnfR7jr0cEszRqN23rb9rsFI4+e0PF\nkB2lbGmD+QoyFWcxvSY5H8RVEwCtEi3UDjwNe0PQDKe5ERiEFS8NqY5+9FZTYk2G\nAex9ec0kiyAqrjbZrOy2djMiDwKBgQDKCRagfiiti63SaAY5AKWK6jnXHOlyz/O/\nbTESFo9R2QQEth6dUtm+XrdY4TeZjfTuYp55jIx/S/smlL5qaYYrWpKFP+R3r6AO\nYyuQcj58YmCvWdZTPrXYzkM8wPLIMmMLHuTvIZclFMiWKDOsC/dOifJg6biJLjGF\noFj6Ynh4EQKBgQCFXOGAaLa/+pH71gSc7wbcPGGaPxrmrOI8bq6Ep6Xa8BsVPw/k\nB2RYuaHDOhxCcmdrDdTaYW0Sd142zfuXlwDjoalRWW8/Y4AONmFKPB2aBMEF/UGh\nJ/mv156TsZnPMZCeHYqYjA05akAnfVS62yq+tYKbUp3VP3E/T+51I9dx+QKBgHoc\nkiOA/R8frHjezNwJKwVSWpFM9UCiteV+nska/5btvwMF/G0EVX09jD3ZKhzSczbe\nPoCi1YxfJTaFcq2oiCKOBL8rBfDdIrVvdTZCBshxQZTajLMV1R1sVbFTwaoE4l4n\nVyG9wLf13uL6+3hCZ0B+GhQ/T30CgYYNi5oSiFOxAoGBAMT7ZJlyG0HUDDkr23BF\nBNR+Q+6VOY3SeCB45CNkqWMwk/HngMjQwDjZsmyCIDIqkfRrH70D9iEFqTX+y7Rt\nW/SmTZMZ9ZjL/Ir/Yqz9cgnXAEccYdbhtZlveZQW+lRq1pUVTNmH4JZ4+E73NaMy\nUh/u1QFV1pxtRt6U3j9lYq6P\n-----END PRIVATE KEY-----\n",
                                    "client_email": "firebase-adminsdk-ks91j@trabajo-autonomo-3-283ba.iam.gserviceaccount.com",
                                    "client_id": "117284635281132318881",
                                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                                    "token_uri": "https://oauth2.googleapis.com/token",
                                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                                    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-ks91j%40trabajo-autonomo-3-283ba.iam.gserviceaccount.com",
                                    "universe_domain": "googleapis.com"
                                },
            "databaseURL" : "https://trabajo-autonomo-3-283ba-default-rtdb.firebaseio.com/"
        }

        firebase = pyrebase.initialize_app(firebaseConfig)
        storage = firebase.storage()

        auth = firebase.auth()

        email = "josue.sauca@unl.edu.ec"
        password = "043708ap9"

        #storage.download('2.jpg', '2.jpg')
        
        print('hola', storage.child('5.jpg').get_url(None))



        
    def traducir_texto(request):

        formulario = FormularioImagen()

        hola = request

        endpoint = 'https://saucajosue.cognitiveservices.azure.com/'
        key = '59fdd9553b4643f29bb2bbb0802aad32'

        #imagenTraduccion = Traduccion.objects.first().imagenTraduccion.url
        
        read_image_url = "https://s.bibliaon.com/es/imagenes/gracias-senor-por-este-nuevo-dia-que-me-permites-comenzar-0.jpg"
        #read_image_url = 'https://firebasestorage.googleapis.com/v0/b/trabajo-autonomo-3-283ba.appspot.com/o/1.png?alt=media&token=57f84b8f-a63b-4b85-b6fa-f83d9de7a92a&_gl=1*1j53n0p*_ga*MTQwOTk2MzM4OS4xNjk3NjQzNDYw*_ga_CW55HF8NVT*MTY5NzY3MTIzNC4yLjEuMTY5NzY3MTUwOC4zOC4wLjA.'
        read_image_url = 'https://cdn0.bodas.com.mx/article/0265/original/1280/png/55620-1.jpeg'
        #read_image_url = 'https://firebasestorage.googleapis.com/v0/b/trabajo-autonomo-3-283ba.appspot.com/o/1.png?alt=media&token=dc668657-1b60-4208-8e73-389bfdac4adc&_gl=1*1h8dh2d*_ga*MTQwOTk2MzM4OS4xNjk3NjQzNDYw*_ga_CW55HF8NVT*MTY5NzY5NjMzMC42LjEuMTY5NzY5NjY1Mi42MC4wLjA.'
        #read_image_url = 'https://images.vexels.com/content/222142/preview/graffiti-alphabet-letter-set-da9351.png'
        #read_image_url = 'https://firebasestorage.googleapis.com/v0/b/trabajo-autonomo-3-283ba.appspot.com/o/home%2Fjosuesauca%2FDocumentos%2FProyecto%20Grupal%2Fsistema_traduccion%2Fmedia%2F1.png?alt=media&token=205a398c-20ab-480b-b3b9-cbe3389a86bf&_gl=1*7zzbfs*_ga*MTQwOTk2MzM4OS4xNjk3NjQzNDYw*_ga_CW55HF8NVT*MTY5NzY5MDg4Ni41LjEuMTY5NzY5MTIzOC40Ny4wLjA.'

        read_image_url = 'https://firebasestorage.googleapis.com/v0/b/trabajo-autonomo-3-283ba.appspot.com/o/5.jpg?alt=media'
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

        return render(hola, "Traducciones/IngresarTraducciones.html",{'form':formulario})




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