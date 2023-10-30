from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group
from django.conf import settings
from datetime import datetime

from .decorators import unauthenticated_user,admin_only
from .models import *
from .forms import *

#librerias para leer texto de imagenes
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials

#Librerias para obtener el idioma de la imagen ingresada
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

from django.contrib.auth.decorators import login_required



from array import array
import os
from PIL import Image
import sys
import time

import requests, uuid, json

#Libreria del firebase
import pyrebase


def PaginaInicio(request):
    return render(request, 'index.html', {})

def obtenerIdiomasTraductor():
    idiomas_lista = []
    #Api idiomas de azure
    url = 'https://api.cognitive.microsofttranslator.com/languages?api-version=3.0'
    response = requests.get(url)
    datos = response.json()
    idiomas_traducciones = datos['translation']

    for key in idiomas_traducciones.items():
        idiomas_lista.append((key[0],key[1]['name']))

    return idiomas_lista

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
    
    @login_required
    def guardar_imagen(request):
        formulario = FormularioImagen()
        idiomas = obtenerIdiomasTraductor()

        if request.method == 'POST':
            formulario = FormularioImagen(request.POST,request.FILES)
            if formulario.is_valid():
                formulario.save()

                AccionesUsuario.guardar_imagen_firebase(str(request.FILES.get('imagenTraduccion')))

                imagen = Imagen.objects.last()
                idiomaTraducir = request.POST.get('idiomas')

                urlImagen = AccionesUsuario.obtener_imagen(imagen)
                print(urlImagen)
                textoTraducido = AccionesUsuario.traducir_texto(urlImagen,idiomaTraducir)

                print(textoTraducido)

                #Crear un objeto de la traduccion que vamos a realizar 
                traduccion = Traduccion.objects.create(idUsuario = request.user,
                                                idImagen = imagen,
                                                horaTraduccion = datetime.now()
                                                ,textoTraduccion = textoTraducido['textoImagen'],
                                                idiomaImagen = textoTraducido['idiomaObtenido'])
                
                numTraduccion = "Traduccion Nr : "+str(Traduccion.objects.count())

                #Crear un objeto de la traduccion obtenida
                traduccionbtenida = TraduccionObtenido.objects.create(idTraduccion = traduccion,
                                                                nombreTraduccionObtenida = numTraduccion,
                                                                textoTraducido = textoTraducido['traduccionRealizada'],
                                                                idiomaTraduccion = idiomaTraducir)

            return render(request, "Traducciones/TraduccionHecha.html",{'traduccionHecha':traduccionbtenida})
        else:
            return render(request, "Traducciones/IngresarImagenTraduccion.html",{'form':formulario,'idiomas':idiomas})
    
    @login_required
    def ver_traducciones_realizadas(request):
        traducciones = Traduccion.objects.filter(idUsuario=request.user)
        traducciones_obtenidas = TraduccionObtenido.objects.filter(idTraduccion__in=traducciones)
        return render(request, "Traducciones/VerTraducciones.html",{'traducciones':traducciones_obtenidas})
    
    def guardar_imagen_firebase(url):
        """
            Configuraciones necesarias para conectarse con la base de datos de 
            firebase para usarla como almacenamiento 
        """
        firebaseConfig = {
            "apiKey": "url_api_custom_firebase",
            "authDomain": "proyecto_url_custom",
            "projectId": "proyect_id",
            "storageBucket": "proyect_configs",
            "messagingSenderId": "proyect_configs",
            "appId": "proyect_configs",
            'serviceAccount' : {
                                    "type": "service_account",
                                    "project_id": "proyect_configs",
                                    "private_key_id": "proyect_configs",
                                    "private_key": "proyect_configs",
                                    "client_email": "firebase-adminsdk-ks91j@trabajo-autonomo-3-283ba.iam.gserviceaccount.com",
                                    "client_id": "proyect_configs",
                                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                                    "token_uri": "https://oauth2.googleapis.com/token",
                                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                                    "client_x509_cert_url": "proyect_configs",
                                    "universe_domain": "googleapis.com"
                                },
            "databaseURL" : "proyect_configs"
        }

        path_imagen = str(url)
        image_name = path_imagen.split('/')[-1]
        firebase = pyrebase.initialize_app(firebaseConfig)
        storage = firebase.storage()
        image_path = os.path.join(settings.MEDIA_ROOT,image_name)
        
        #Almacenamos la imagen obtenida en la base de datos de firebase
        storage.child(url).put(image_path) 

    def obtener_imagen(imagen):
        firebaseConfig = {
            "apiKey": "proyect_configs",
            "authDomain": "proyect_configs",
            "projectId": "proyect_configs",
            "storageBucket": "proyect_configs,
            "messagingSenderId": "proyect_configs",
            "appId": "proyect_configs",
            'serviceAccount' : {
                                    "type": "service_account",
                                    "project_id": "proyect_configs",
                                    "private_key_id": "proyect_configs",
                                    "private_key": "proyect_configs",
                                    "client_email": "proyect_configs",
                                    "client_id": "proyect_configs",
                                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                                    "token_uri": "https://oauth2.googleapis.com/token",
                                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                                    "client_x509_cert_url": "proyect_configs",
                                    "universe_domain": "googleapis.com"
                                },
            "databaseURL" : "proyect_configs"
        }

        firebase = pyrebase.initialize_app(firebaseConfig)
        storage = firebase.storage()
        return storage.child(str(imagen)).get_url(None)

    def traducir_texto(urlImagen,idiomaTraducir):

        endpoint = 'url_custom_service'
        key = 'key_custom'
       
        computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(key))
        print("===== Read File - remote =====")
        read_response = computervision_client.read(urlImagen, raw=True)
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
        #print("palabras obtenidas ", palabras_imagen)

        #Obtener el idioma de la imagen a traducir
        client = AccionesUsuario.authenticate_client()
        idiomaObtenido = AccionesUsuario.language_detection_example(client,palabras_imagen)
        idiomaObtenido = idiomaObtenido['primary_language']['iso6391_name']

        #Traduccir el texto obtenido
        endpoint = 'url_custom_service'
        key = 'key_custom'
        location = 'eastus'

        path = '/translate'
        constructed_url = endpoint + path
        params = {
            'api-version': '3.0',
            'from': ''+idiomaObtenido,
            'to': [''+idiomaTraducir]
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
        return {'traduccionRealizada' : str(response[0]['translations'][0]['text'])
                ,'textoImagen':palabras_imagen ,
                'idiomaObtenido':idiomaObtenido}  
    
    # Authenticate the client using your key and endpoint 
    def authenticate_client():
        endpoint = 'url_custom_service'
        key = 'key_service'
        ta_credential = AzureKeyCredential(key)
        text_analytics_client = TextAnalyticsClient(
                endpoint=endpoint, 
                credential=ta_credential)
        return text_analytics_client

    # Example method for detecting the language of text
    def language_detection_example(client,textoObtenido):
        try:
            documents = [textoObtenido+""]
            response = client.detect_language(documents = documents, country_hint = 'us')[0]
            return response
        except Exception as err:
            print("Encountered exception. {}".format(err))
