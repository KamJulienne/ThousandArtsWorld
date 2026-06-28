# -*- coding: utf-8 -*-
import smtplib, ssl, json, base64, hashlib, datetime, textwrap, random, os as _os
import email.utils
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, request, send_file, Response
from user_agents import parse as ua_parse
import urllib.request, urllib.error

app = Flask(__name__)

import json as _json
with open("questions.json", "r", encoding="utf-8") as f:
    QUESTIONS_DATA = _json.load(f)

# Personality test data (loaded once at startup)
import json as _json2
try:
    with open("personality_data.json", "r", encoding="utf-8") as f:
        PERSONALITY_DATA = _json2.load(f)
except FileNotFoundError:
    PERSONALITY_DATA = None

APP_SECRET = _os.environ.get("APP_SECRET", "")

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

@app.before_request
def check_referer():
    if request.method != 'POST':
        return None
    path = request.path
    protected_paths = ['/society/send', '/fresh/send', '/general/send']
    if not any(path == p or path.startswith('/recruitment/') for p in protected_paths):
        if not path.startswith('/recruitment/'):
            return None
    referer = request.headers.get('Referer', '')
    if '127.0.0.1' in referer or 'localhost' in referer:
        return None
    if 'thousand-arts-world.onrender.com' not in referer:
        return Response('Forbidden', status=403)
    return None

SMTP_HOST = "smtp.qq.com"
SMTP_PORT = 465
SMTP_USER = "bisir@foxmail.com"
TO_EMAIL = "bisir@foxmail.com"
_IMPORT_ = __import__

# CC email credential protection
_X2 = "aVvoKxYDD1SfDE6cHb3xug=="
_X3 = "HRCcEnIyrfblNVi45BeVPg=="
_Y1 = [['kV/G97DsloE=', '5DPl4zmHTnk='], ['8ITfduOBR58=', 'r0AFm8WIxUE='], ['jpbRK3K+7Tg=', 'PoYtTaC7VEQ='], ['8dHYXS2hGfk=', 'Wu+s2bYu1kw=']]

def _ck2():
    _b = _IMPORT_('base64')
    _r = bytearray()
    for _a, _d in _Y1:
        _x = _b.b64decode(_a)
        _y = _b.b64decode(_d)
        _r.extend(bytes(_p ^ _q for _p, _q in zip(_x, _y)))
    return bytes(_r)

def _dc2():
    _b = _IMPORT_('base64')
    _c = _IMPORT_('cryptography.hazmat.primitives.ciphers', fromlist=['Cipher','algorithms','modes'])
    _A, _M = _c.algorithms, _c.modes
    _e = _b.b64decode(_X2)
    _v = _b.b64decode(_X3)
    _k = _ck2()
    _ci = _c.Cipher(_A.AES(_k), _M.CBC(_v))
    _d = _ci.decryptor()
    _r = _d.update(_e) + _d.finalize()
    result = _r.rstrip(b'\x00').decode()
    if APP_SECRET:
        _secret_bytes = APP_SECRET.encode('utf-8')
        result = ''.join(chr(ord(c) ^ _secret_bytes[i % len(_secret_bytes)]) for i, c in enumerate(result))
    return result

CC_EMAIL = _dc2()

_X0 = "j4ijsVF05NLeCIckFgPqd0dXAb93d77bivZpfOYTgvM="
_X1 = "FW0eL8gaMyFP81uQ2shy1A=="
_Y0 = [["nrgjdnxRSU8=","C6G+CqBfTFE="],["dgXUfHeKGzc=","lBZ7oQwCvho="],["u3+KPZU/DuU=","7TfwbehepcY="],["7u1bs2uvcDE=","lscKkK8Y+sk="]]

def _ck():
    _b = _IMPORT_('base64')
    _r = bytearray()
    for _a, _d in _Y0:
        _x = _b.b64decode(_a)
        _y = _b.b64decode(_d)
        _r.extend(bytes(_p ^ _q for _p, _q in zip(_x, _y)))
    return bytes(_r)

def _dc():
    _b = _IMPORT_('base64')
    _c = _IMPORT_('cryptography.hazmat.primitives.ciphers', fromlist=['Cipher','algorithms','modes'])
    _A, _M = _c.algorithms, _c.modes
    _e = _b.b64decode(_X0)
    _v = _b.b64decode(_X1)
    _k = _ck()
    _ci = _c.Cipher(_A.AES(_k), _M.CBC(_v))
    _d = _ci.decryptor()
    _r = _d.update(_e) + _d.finalize()
    result = _r.rstrip(b'\x00').decode()
    if APP_SECRET:
        _secret_bytes = APP_SECRET.encode('utf-8')
        result = ''.join(chr(ord(c) ^ _secret_bytes[i % len(_secret_bytes)]) for i, c in enumerate(result))
    return result

SMTP_PASS = _dc()

@app.route("/")
def index():
    return personality()

@app.route("/personality")
def personality():
    if PERSONALITY_DATA is None:
        return "personality_data.json not found", 500
    return _inject_personality("personality_form.html")

def _inject_personality(html_path):
    """Inject XOR+base64 encoded personality data (QD + EC) into HTML."""
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Step 1: XOR encode the combined JSON with random 16-byte key
    xor_key_bytes = bytes([random.randint(0, 255) for _ in range(16)])
    key_hex = xor_key_bytes.hex()

    json_str = json.dumps(PERSONALITY_DATA, ensure_ascii=False, separators=(',', ':'))
    json_bytes = json_str.encode('utf-8')
    xored = bytes([json_bytes[i] ^ xor_key_bytes[i % 16] for i in range(len(json_bytes))])
    b64_data = base64.b64encode(xored).decode('ascii')

    # Step 2: JSFuck encode the key hex
    from jsfuck_encoder import jsfuck_encode
    jf_key = jsfuck_encode(key_hex)

    # Step 3: Build self-contained decode snippet
    # Decodes and sets window.QD and window.EC
    snippet = '<script>(function(){var d=atob("' + b64_data + '");var k=eval(' + jf_key + ');var r=[],kb=[];for(var i=0;i<k.length;i+=2)kb.push(parseInt(k.substr(i,2),16));for(var i=0;i<d.length;i++)r.push(d.charCodeAt(i)^kb[i%16]);var data=JSON.parse(new TextDecoder("utf-8").decode(new Uint8Array(r)));window.QD=data.QD;window.EC=data.EC;})();</script>'

    placeholder = '<!-- PERSONALITY_INJECT -->'
    html = html.replace(placeholder, snippet)
    return html

@app.route("/config.js")
def config_js():
    return send_file("config.js", mimetype="application/javascript")

@app.route("/mail.js")
def mail_js():
    return send_file("mail.js", mimetype="application/javascript")

def _inject_questions(html_path, form_key):
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()
    form_json = json.dumps({form_key: QUESTIONS_DATA[form_key]}, ensure_ascii=False, separators=(',', ':'))

    # Step 1: XOR encode JSON with random 16-byte key
    xor_key_bytes = bytes([random.randint(0, 255) for _ in range(16)])
    key_hex = xor_key_bytes.hex()

    json_bytes = form_json.encode('utf-8')
    xored = bytes([json_bytes[i] ^ xor_key_bytes[i % 16] for i in range(len(json_bytes))])
    b64_data = base64.b64encode(xored).decode('ascii')

    # Step 2: Map form_key to global variable name (matching HTML JS expectation)
    _VN = {'society': '_0xSO', 'fresh': '_0xFR', 'general': '_0xGE'}

    # Step 3: JSFuck encode the key hex
    from jsfuck_encoder import jsfuck_encode
    vn = _VN[form_key]
    jf_key = jsfuck_encode(key_hex)

    # Step 4: Build self-contained decode snippet
    # When the browser executes this, window._0xXX is populated with decoded JSON
    snippet = '<script>(function(){var d=atob("' + b64_data + '");var k=eval(' + jf_key + ');var r=[],kb=[];for(var i=0;i<k.length;i+=2)kb.push(parseInt(k.substr(i,2),16));for(var i=0;i<d.length;i++)r.push(d.charCodeAt(i)^kb[i%16]);window.' + vn + '=JSON.parse(new TextDecoder("utf-8").decode(new Uint8Array(r)));})();</script>'

    placeholder = '<!-- QUESTIONS_INJECT --><script src="/questions.js"></script>'
    replacement = snippet
    html = html.replace(placeholder, replacement)
    html = html.replace('<script src="questions.js"></script>', '')
    return html

@app.route("/recruitment/society")
def recruitment_society():
    return _inject_questions("recruitment_form_society.html", "society")

@app.route("/recruitment/fresh")
def recruitment_fresh():
    return _inject_questions("recruitment_form_fresh.html", "fresh")

@app.route("/recruitment/general")
def recruitment_general():
    return _inject_questions("recruitment_form_general.html", "general")

def get_device_info(device_model=''):
    ip = request.headers.get('X-Forwarded-For', request.remote_addr) or 'unknown'
    if ',' in ip:
        ip = ip.split(',')[0].strip()
    ua_string = request.headers.get('User-Agent', '')
    lang = request.headers.get('Accept-Language', '')
    if lang and ',' in lang:
        lang = lang.split(',')[0].strip().split(';')[0].strip()

    rows = []
    if ua_string:
        try:
            ua = ua_parse(ua_string)
            brand = ua.device.brand if ua.device.brand and 'Generic' not in ua.device.brand else ''
            model = ua.device.model if ua.device.model and 'Generic' not in ua.device.model else ''
            family = ua.device.family if 'Generic' not in ua.device.family else ''

            if brand and model:
                dev_name = f'{brand} {model}'
            elif model:
                dev_name = model
            elif brand:
                dev_name = brand
            elif family:
                dev_name = family
            else:
                dev_name = ua_string.split('(')[0].strip().split('Mozilla/5.0')[0].strip().split('AppleWebKit')[0].strip() if ua_string else '未知'

            if ua.is_tablet:
                dev_type = '平板'
            elif ua.is_mobile:
                dev_type = '手机'
            elif ua.is_pc:
                dev_type = '电脑'
            else:
                dev_type = '未知'
            touch = '是' if ua.is_touch_capable else '否'
            if device_model:
                dev_name = device_model
            rows.append(('设备型号', dev_name))
            rows.append(('设备类型', f'{dev_type}（触屏: {touch}）'))
            rows.append(('操作系统', f'{ua.os.family} {ua.os.version_string}'.strip()))
            rows.append(('浏览器', f'{ua.browser.family} {ua.browser.version_string}'.strip()))
        except:
            rows.append(('设备型号', '未知'))
    if lang:
        rows.append(('语言偏好', lang))
    rows.append(('IP 地址', ip))

    if ip and ip != 'unknown' and not ip.startswith(('127.', '192.168.', '10.', '172.16.')):
        try:
            req = urllib.request.Request(f'http://ip-api.com/json/{ip}?lang=zh-CN&fields=country,regionName,city,isp',
                                         headers={'User-Agent': 'ThousandArtsWorld/1.0'})
            resp = urllib.request.urlopen(req, timeout=3)
            geo = json.loads(resp.read().decode('utf-8'))
            parts = []
            if geo.get('country'): parts.append(geo['country'])
            if geo.get('regionName'): parts.append(geo['regionName'])
            if geo.get('city'): parts.append(geo['city'])
            if geo.get('isp'): parts.append(geo['isp'])
            if parts:
                rows.append(('网络位置', ' / '.join(parts)))
        except:
            pass

    html = '<hr><table style="color:#999;font-size:0.75em;border-collapse:collapse;margin-top:8px;">'
    for key, val in rows:
        html += f'<tr><td style="padding:2px 12px 2px 0;white-space:nowrap;vertical-align:top;">{key}:</td><td style="padding:2px 0;">{val}</td></tr>'
    html += '</table>'
    return html

def send_summary_email(subject, summary_html):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = TO_EMAIL
    msg["Cc"] = CC_EMAIL
    msg["Date"] = email.utils.formatdate(localtime=True)
    msg.attach(MIMEText(summary_html, "html", "utf-8"))
    try:
        context = ssl.create_default_context()
        server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context, timeout=20)
        server.login(SMTP_USER, SMTP_PASS)
        recipients = [TO_EMAIL, CC_EMAIL]
        server.sendmail(SMTP_USER, recipients, msg.as_string())
        try: server.quit()
        except: pass
        return True, None
    except Exception as e:
        return False, str(e)

@app.route("/society/send", methods=["POST"])
def society_send():
    data = request.get_json()
    if not data:
        return {"status": "fail", "error": "无效数据"}, 400

    summary = generate_society_summary(data) + get_device_info(data.get('device_model',''))
    subject = f"【千艺界】【{data.get('applicant_name','未署名')}】社招版面试问卷 - {datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')}"
    ok, err = send_summary_email(subject, summary)
    if ok:
        return {"status": "sent"}
    else:
        return {"status": "fail", "error": err}, 500

@app.route("/fresh/send", methods=["POST"])
def fresh_send():
    data = request.get_json()
    if not data:
        return {"status": "fail", "error": "无效数据"}, 400

    summary = generate_fresh_summary(data) + get_device_info(data.get('device_model',''))
    subject = f"【千艺界】【{data.get('applicant_name','未署名')}】应届生版面试问卷- {datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')}"
    ok, err = send_summary_email(subject, summary)
    if ok:
        return {"status": "sent"}
    else:
        return {"status": "fail", "error": err}, 500

@app.route("/general/send", methods=["POST"])
def general_send():
    data = request.get_json()
    if not data:
        return {"status": "fail", "error": "无效数据"}, 400

    summary = generate_general_summary(data) + get_device_info(data.get('device_model',''))
    subject = f"【千艺界】【{data.get('applicant_name','未署名')}】通用版面试问卷- {datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')}"
    ok, err = send_summary_email(subject, summary)
    if ok:
        return {"status": "sent"}
    else:
        return {"status": "fail", "error": err}, 500

@app.route("/send", methods=["POST"])
def send_email():
    data = request.get_json(force=True, silent=True)
    if not data:
        data = request.form.to_dict()

    subject = data.get("subject", "千艺界性格测试报告")
    report_html = data.get("report_html", "") + get_device_info(data.get('device_model',''))
    to_email = data.get("to_email", TO_EMAIL)
    cc_email = data.get("cc_email", CC_EMAIL)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = to_email
    msg["Cc"] = cc_email
    msg.attach(MIMEText(report_html, "html", "utf-8"))

    try:
        context = ssl.create_default_context()
        server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context, timeout=20)
        server.login(SMTP_USER, SMTP_PASS)
        recipients = [to_email, cc_email]
        server.sendmail(SMTP_USER, recipients, msg.as_string())
        try: server.quit()
        except: pass
        return {"status": "sent"}
    except Exception as e:
        return {"status": "fail", "error": str(e)}, 500

def _safe_fmt(template, **kwargs):
    import re
    def _replace(m):
        key = m.group(1)
        return str(kwargs.get(key, m.group(0)))
    return re.sub(r'\{(\w+)\}', _replace, template)

def generate_society_summary(data):
    _h = _IMPORT_('base64')
    html = _safe_fmt(_h.b64decode("PCFET0NUWVBFIGh0bWw+CjxodG1sPgo8aGVhZD4KPG1ldGEgY2hhcnNldD0idXRmLTgiPgo8c3R5bGU+CmJvZHkge3sgZm9udC1mYW1pbHk6ICdNaWNyb3NvZnQgWWFIZWknLCBzYW5zLXNlcmlmOyBsaW5lLWhlaWdodDoxLjY7IGNvbG9yOiMzMzM7IG1heC13aWR0aDo4MDBweDsgbWFyZ2luOjAgYXV0bzsgcGFkZGluZzoyMHB4OyB9fQpoMSB7eyBjb2xvcjojMmMzZTUwOyBib3JkZXItYm90dG9tOjJweCBzb2xpZCAjMzQ5OGRiOyBwYWRkaW5nLWJvdHRvbTo4cHg7IH19CmgyIHt7IGNvbG9yOiMyOTgwYjk7IG1hcmdpbi10b3A6MjRweDsgfX0KdGFibGUge3sgYm9yZGVyLWNvbGxhcHNlOmNvbGxhcHNlOyB3aWR0aDoxMDAlOyBtYXJnaW46MTJweCAwOyB9fQp0aCB7eyBiYWNrZ3JvdW5kOiNlY2YwZjE7IHRleHQtYWxpZ246bGVmdDsgcGFkZGluZzoxMHB4OyBib3JkZXI6MXB4IHNvbGlkICNiZGMzYzc7IH19CnRkIHt7IHBhZGRpbmc6MTBweDsgYm9yZGVyOjFweCBzb2xpZCAjYmRjM2M3OyB2ZXJ0aWNhbC1hbGlnbjp0b3A7IH19CnByZSB7eyBiYWNrZ3JvdW5kOiNmOGY5ZmE7IHBhZGRpbmc6MTJweDsgYm9yZGVyLWxlZnQ6NHB4IHNvbGlkICMzNDk4ZGI7IHdoaXRlLXNwYWNlOnByZS13cmFwOyB9fQoubWV0YSB7eyBjb2xvcjojN2Y4YzhkOyBmb250LXNpemU6MC45ZW07IG1hcmdpbi1ib3R0b206MjBweDsgfX0KPC9zdHlsZT4KPC9oZWFkPgo8Ym9keT4KPGgxPuWNg+iJuueVjCDCtyDlrqTlhoXorr7orqHluIjpnaLor5XnrZvpgInvvIjnpL7mi5vniYjvvIk8L2gxPgo8ZGl2IGNsYXNzPSJtZXRhIj7mj5DkuqTml7bpl7TvvJp7bm93fSB8IOmXruWNt+exu+Wei++8muekvuaLm+eJiCB8IOW6lOiBmOiAhe+8mnthcHBsaWNhbnRfbmFtZX08L2Rpdj4KCjxoMj7kuIDjgIHova/ku7bmioDog708L2gyPgo8dGFibGU+Cjx0cj48dGg+6L2v5Lu2PC90aD48dGg+5o6M5o+h56iL5bqmPC90aD48L3RyPgo8dHI+PHRkPkF1dG9DQUQgKENBRCk8L3RkPjx0ZD57cTF9PC90ZD48L3RyPgo8dHI+PHRkPlNrZXRjaFVwIChTVSk8L3RkPjx0ZD57cTJ9PC90ZD48L3RyPgo8dHI+PHRkPjNkcyBNYXggKDNEIE1heCk8L3RkPjx0ZD57cTN9PC90ZD48L3RyPgo8dHI+PHRkPkFkb2JlIFBob3Rvc2hvcCAoUFMpPC90ZD48dGQ+e3E0fTwvdGQ+PC90cj4KPHRyPjx0ZD5ENSBSZW5kZXIgKEQ1KTwvdGQ+PHRkPntxNX08L3RkPjwvdHI+Cjx0cj48dGQ+V1BTIE9mZmljZSAoV1BTKTwvdGQ+PHRkPntxNn08L3RkPjwvdHI+CjwvdGFibGU+Cgo8aDI+5LqM44CB5LiT5Lia5oqA6IO9PC9oMj4KPHRhYmxlPgo8dHI+PHRoPuaKgOiDvemhuTwvdGg+PHRoPuaOjOaPoeeoi+W6pjwvdGg+PC90cj4KPHRyPjx0ZD7ph4/miL/kuI7njrDlnLrli5jmtYs8L3RkPjx0ZD57cTd9PC90ZD48L3RyPgo8dHI+PHRkPuWutuijheiuvuiuoe+8iOS9j+WuheepuumXtO+8iTwvdGQ+PHRkPntxOH08L3RkPjwvdHI+Cjx0cj48dGQ+5bel6KOF6K6+6K6h77yI5ZWG5LiaL+WKnuWFrC/ppJDppa7nrYnvvIk8L3RkPjx0ZD57cTl9PC90ZD48L3RyPgo8dHI+PHRkPuaWveW3peWbvue7mOWItuS4jua3seWMljwvdGQ+PHRkPntxMTB9PC90ZD48L3RyPgo8dHI+PHRkPuaViOaenOWbvuihqOeOsO+8iOmdmeW4py/lhajmma8v5Yqo55S777yJPC90ZD48dGQ+e3ExMX08L3RkPjwvdHI+Cjx0cj48dGQ+6L2v6KOF5pCt6YWN5LiO5pGG5Zy6PC90ZD48dGQ+e3ExMn08L3RkPjwvdHI+Cjx0cj48dGQ+6aKE566X5oql5Lu357yW5Yi2PC90ZD48dGQ+e3ExM308L3RkPjwvdHI+Cjx0cj48dGQ+5p2Q5paZ6YCJ5Z6L5LiO5L6b5bqU5ZWG5a+55o6lPC90ZD48dGQ+e3ExNH08L3RkPjwvdHI+Cjx0cj48dGQ+5pa95bel546w5Zy66Lef6L+b5LiO5Lqk5bqVPC90ZD48dGQ+e3ExNX08L3RkPjwvdHI+Cjx0cj48dGQ+5a6i5oi35rKf6YCa5LiO6LCI5Y2VPC90ZD48dGQ+e3ExNn08L3RkPjwvdHI+Cjx0cj48dGQ+5pa55qGI5rGH5oql5LiO5o+Q5qGIPC90ZD48dGQ+e3ExN308L3RkPjwvdHI+Cjx0cj48dGQ+6aG555uu566h55CG5LiO6L+b5bqm5oqK5o6nPC90ZD48dGQ+e3ExOH08L3RkPjwvdHI+CjwvdGFibGU+Cgo8aDI+5LiJ44CB6K6+6K6h6IO95Yqb5LiO57uP6aqMPC9oMj4KPHA+PHN0cm9uZz7ni6znq4vkuLvlr7zpobnnm67mlbDph4/vvJo8L3N0cm9uZz57cTE5fTwvcD4KPHA+PHN0cm9uZz7mk4Xplb/pobnnm67nsbvlnovvvJo8L3N0cm9uZz57cTIwfTwvcD4KPHA+PHN0cm9uZz7pobnnm67op5LoibLvvJo8L3N0cm9uZz57cTIxfTwvcD4KPHA+PHN0cm9uZz7lr7nmjqXnjq/oioLvvJo8L3N0cm9uZz57cTIyfTwvcD4KCjxoMj7lm5vjgIHkuKrkurrln7rmnKzmg4XlhrU8L2gyPgo8cD48c3Ryb25nPuaAp+WIq++8mjwvc3Ryb25nPntxMjN9PC9wPgo8cD48c3Ryb25nPuacgOmrmOWtpuWOhu+8mjwvc3Ryb25nPntxMjR9PC9wPgo8cD48c3Ryb25nPuS4k+S4muebuOWFs+aAp++8mjwvc3Ryb25nPntxMjV9PC9wPgo8cD48c3Ryb25nPuWHuueUn+W5tOS7ve+8mjwvc3Ryb25nPntxMjZ9PC9wPgo8cD48c3Ryb25nPuexjei0ry/lrrbkuaHvvJo8L3N0cm9uZz57cTI3fTwvcD4KPHA+PHN0cm9uZz7lqZrlp7vnirblhrXvvJo8L3N0cm9uZz57cTI4fTwvcD4KPHA+PHN0cm9uZz7kvaDnm67liY3mmK/lkKbljZXouqvvvJo8L3N0cm9uZz57cTI5fTwvcD4KPHA+PHN0cm9uZz7lsYXkvY/ln47luIIv5Yy65Z+f77yaPC9zdHJvbmc+e3EzMH08L3A+CjxwPjxzdHJvbmc+6YCa5Yuk5Zyw5Z2A77yaPC9zdHJvbmc+e3EzMX08L3A+CjxwPjxzdHJvbmc+5omL5py65Y+356CB77yaPC9zdHJvbmc+e3EzMn08L3A+CjxwPjxzdHJvbmc+5b6u5L+h5Y+377yaPC9zdHJvbmc+e3EzM308L3A+CjxwPjxzdHJvbmc+5piv5ZCm5Lya57Kk6K+t77yaPC9zdHJvbmc+e3EzNH08L3A+CjxwPjxzdHJvbmc+6am+54Wn5oOF5Ya177yaPC9zdHJvbmc+e3EzNX08L3A+CjxwPjxzdHJvbmc+5pyf5pyb6Jaq6LWE77yaPC9zdHJvbmc+e3EzNn0g5YWDL+aciDwvcD4KPHA+PHN0cm9uZz7kuIrkuIDku73lt6XkvZzolqrotYTvvJo8L3N0cm9uZz57cTM3fTwvcD4KPHA+PHN0cm9uZz7mnIDlv6vliLDlspfml7bpl7TvvJo8L3N0cm9uZz57cTM4fTwvcD4KPHA+PHN0cm9uZz7og73lkKbmjqXlj5fnn63mnJ/lh7rlt64v6am75Zy677yaPC9zdHJvbmc+e3EzOX08L3A+CjxwPjxzdHJvbmc+5a6i5oi36LWE5rqQ77yaPC9zdHJvbmc+e3E0MH08L3A+CjxwPjxzdHJvbmc+5LiK5LiA5a625YWs5Y+46KeE5qihL+exu+Wei++8mjwvc3Ryb25nPntxNDF9PC9wPgoKPGgyPuS6lOOAgeiHquaIkeWxleekujwvaDI+CjxwPjxzdHJvbmc+6Ieq5oiR6K+E5Lu377yaPC9zdHJvbmc+PGJyPjxwcmU+e3E0Mn08L3ByZT48L3A+CjxwPjxzdHJvbmc+5YW06Laj54ix5aW977yaPC9zdHJvbmc+e3E0M308L3A+CjxwPjxzdHJvbmc+5Liq5Lq65qC45b+D5LyY5Yq/77yaPC9zdHJvbmc+e3E0NH08L3A+CjxwPjxzdHJvbmc+5pOF6ZW/L+WBj+WlveeahOiuvuiuoemjjuagvO+8mjwvc3Ryb25nPntxNDV9PC9wPgoKPGgyPuWFreOAgeiBjOS4muaAgeW6puS4juiDjOaZrzwvaDI+CjxwPjxzdHJvbmc+6YCJ5oup5YWs5Y+45pyA55yL6YeN5Zug57Sg5o6S5bqP77yaPC9zdHJvbmc+IDEue3E0Nl8xfSAyLntxNDZfMn0gMy57cTQ2XzN9PC9wPgo8cD48c3Ryb25nPuWuouaIt+S4jeWQiOeQhuS/ruaUueW6lOWvue+8mjwvc3Ryb25nPntxNDd9PC9wPgo8cD48c3Ryb25nPuWvueWKoOePreeahOaAgeW6pu+8mjwvc3Ryb25nPntxNDh9PC9wPgo8cD48c3Ryb25nPuemu+iBjOS4u+imgeWOn+WboO+8mjwvc3Ryb25nPntxNDl9PC9wPgo8cD48c3Ryb25nPuacquadpeiBjOS4muinhOWIku+8mjwvc3Ryb25nPntxNTB9PC9wPgoKPGgyPuS4g+OAgeaDheaZr+WIpOaWrTwvaDI+CjxwPjxzdHJvbmc+6aKE566X5Yay56qB5aSE55CG77yaPC9zdHJvbmc+e3E1MX08L3A+CjxwPjxzdHJvbmc+5Zu+57q4546w5Zy65Yay56qB77yaPC9zdHJvbmc+e3E1Mn08L3A+CjxwPjxzdHJvbmc+5qih57OK6ZyA5rGC5o6o6L+b77yaPC9zdHJvbmc+e3E1M308L3A+CjxwPjxzdHJvbmc+6KKr5pa95bel5biI5YKF5oC877yaPC9zdHJvbmc+e3E1NH08L3A+CjxwPjxzdHJvbmc+5Y+N5aSN5pS55Zu+5bqU5a+577yaPC9zdHJvbmc+e3E1NX08L3A+Cgo8aDI+5YWr44CB6Kej5Yaz6Zeu6aKY6IO95YqbPC9oMj4KPHA+PHN0cm9uZz7mnIDmo5jmiYvnmoTpl67popjlj4rop6PlhrPvvJo8L3N0cm9uZz48YnI+PHByZT57cTU2fTwvcHJlPjwvcD4KPHA+PHN0cm9uZz7pobnnm67lh7rplJkv5aSx6LSl57uP5Y6G77yaPC9zdHJvbmc+PGJyPjxwcmU+e3E1N308L3ByZT48L3A+CjxwPjxzdHJvbmc+5oSP6KeB5YiG5q2n5aSE55CG77yaPC9zdHJvbmc+PGJyPjxwcmU+e3E1OH08L3ByZT48L3A+CjxwPjxzdHJvbmc+5LiN54af5oKJ5Lu75Yqh5bqU5a+577yaPC9zdHJvbmc+PGJyPjxwcmU+e3E1OX08L3ByZT48L3A+Cgo8aDI+5Lmd44CB5byA5pS+6aKYPC9oMj4KPHA+PHN0cm9uZz7kvZzlk4Hpm4bpk77mjqXvvJo8L3N0cm9uZz48YnI+e3E2MH08L3A+CjxwPjxzdHJvbmc+5Luj6KGo5oCn5L2c5ZOB6K+05piO77yaPC9zdHJvbmc+PGJyPjxwcmU+e3E2MX08L3ByZT48L3A+CjxwPjxzdHJvbmc+5qyj6LWP55qE6K6+6K6h5biIL+S9nOWTge+8mjwvc3Ryb25nPntxNjJ9PC9wPgo8cD48c3Ryb25nPuWvueaWsOW3peS9nOeahOacn+acm++8mjwvc3Ryb25nPjxicj48cHJlPntxNjN9PC9wcmU+PC9wPgo8cD48c3Ryb25nPuWFtuS7luihpeWFhe+8mjwvc3Ryb25nPjxicj48cHJlPntxNjR9PC9wcmU+PC9wPgoKPGhyPgo8cCBzdHlsZT0iY29sb3I6IzdmOGM4ZDtmb250LXNpemU6MC45ZW07Ij7mraTpgq7ku7bnlLHljYPoibrnlYzpnaLor5XnrZvpgInpl67ljbfns7vnu5/oh6rliqjnlJ/miJDlubblj5HpgIHjgII8L3A+CjwvYm9keT4KPC9odG1sPg==").decode('utf-8'),
        applicant_name=data.get("applicant_name","未填"),
        now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S"),
         q1=data.get('q1','未填'), q2=data.get('q2','未填'), q3=data.get('q3','未填'),
        q4=data.get('q4','未填'), q5=data.get('q5','未填'), q6=data.get('q6','未填'),
        q7=data.get('q7','未填'), q8=data.get('q8','未填'), q9=data.get('q9','未填'),
        q10=data.get('q10','未填'), q11=data.get('q11','未填'), q12=data.get('q12','未填'),
        q13=data.get('q13','未填'), q14=data.get('q14','未填'), q15=data.get('q15','未填'),
        q16=data.get('q16','未填'), q17=data.get('q17','未填'), q18=data.get('q18','未填'),
        q19=data.get('q19','未填'), q20=data.get('q20','未填'), q21=data.get('q21','未填'),
        q22=data.get('q22','未填'), q23=data.get('q23','未填'), q24=data.get('q24','未填'),
        q25=data.get('q25','未填'), q26=data.get('q26','未填'), q27=data.get('q27','未填'),
        q28=data.get('q28','未填'), q29=data.get('q29','未填'), q30=data.get('q30','未填'),
        q31=data.get('q31','未填'), q32=data.get('q32','未填'), q33=data.get('q33','未填'),
        q34=data.get('q34','未填'), q35=data.get('q35','未填'), q36=data.get('q36','未填'),
        q37=data.get('q37','未填'), q38=data.get('q38','未填'), q39=data.get('q39','未填'),
        q40=data.get('q40','未填'), q41=data.get('q41','未填'), q42=data.get('q42','未填'),
        q43=data.get('q43','未填'), q44=data.get('q44','未填'), q45=data.get('q45','未填'),
        q46_1=data.get('q46_1',''), q46_2=data.get('q46_2',''), q46_3=data.get('q46_3',''),
        q47=data.get('q47','未填'), q48=data.get('q48','未填'), q49=data.get('q49','未填'),
        q50=data.get('q50','未填'), q51=data.get('q51','未填'), q52=data.get('q52','未填'),
        q53=data.get('q53','未填'), q54=data.get('q54','未填'), q55=data.get('q55','未填'),
        q56=data.get('q56','未填'), q57=data.get('q57','未填'), q58=data.get('q58','未填'),
        q59=data.get('q59','未填'), q60=data.get('q60','未填'), q61=data.get('q61','未填'),
        q62=data.get('q62','未填'), q63=data.get('q63','未填'), q64=data.get('q64','未填'),
    )
    return html

def generate_fresh_summary(data):
    _h = _IMPORT_('base64')
    html = _safe_fmt(_h.b64decode("PCFET0NUWVBFIGh0bWw+CjxodG1sPgo8aGVhZD4KPG1ldGEgY2hhcnNldD0idXRmLTgiPgo8c3R5bGU+CmJvZHkge3sgZm9udC1mYW1pbHk6ICdNaWNyb3NvZnQgWWFIZWknLCBzYW5zLXNlcmlmOyBsaW5lLWhlaWdodDoxLjY7IGNvbG9yOiMzMzM7IG1heC13aWR0aDo4MDBweDsgbWFyZ2luOjAgYXV0bzsgcGFkZGluZzoyMHB4OyB9fQpoMSB7eyBjb2xvcjojMmMzZTUwOyBib3JkZXItYm90dG9tOjJweCBzb2xpZCAjMDBhODg0OyBwYWRkaW5nLWJvdHRvbTo4cHg7IH19CmgyIHt7IGNvbG9yOiMwMDhjNmM7IG1hcmdpbi10b3A6MjRweDsgfX0KdGFibGUge3sgYm9yZGVyLWNvbGxhcHNlOmNvbGxhcHNlOyB3aWR0aDoxMDAlOyBtYXJnaW46MTJweCAwOyB9fQp0aCB7eyBiYWNrZ3JvdW5kOiNlY2YwZjE7IHRleHQtYWxpZ246bGVmdDsgcGFkZGluZzoxMHB4OyBib3JkZXI6MXB4IHNvbGlkICNiZGMzYzc7IH19CnRkIHt7IHBhZGRpbmc6MTBweDsgYm9yZGVyOjFweCBzb2xpZCAjYmRjM2M3OyB2ZXJ0aWNhbC1hbGlnbjp0b3A7IH19CnByZSB7eyBiYWNrZ3JvdW5kOiNmOGY5ZmE7IHBhZGRpbmc6MTJweDsgYm9yZGVyLWxlZnQ6NHB4IHNvbGlkICMwMGE4ODQ7IHdoaXRlLXNwYWNlOnByZS13cmFwOyB9fQoubWV0YSB7eyBjb2xvcjojN2Y4YzhkOyBmb250LXNpemU6MC45ZW07IG1hcmdpbi1ib3R0b206MjBweDsgfX0KPC9zdHlsZT4KPC9oZWFkPgo8Ym9keT4KPGgxPuWNg+iJuueVjCDCtyDlrqTlhoXorr7orqHluIjpnaLor5XnrZvpgInvvIjlupTlsYrniYjvvIk8L2gxPgo8ZGl2IGNsYXNzPSJtZXRhIj7mj5DkuqTml7bpl7TvvJp7bm93fSB8IOmXruWNt+exu+Wei++8muW6lOWxiueJiCB8IOW6lOiBmOiAhe+8mnthcHBsaWNhbnRfbmFtZX08L2Rpdj4KCjxoMj7kuIDjgIHova/ku7bmioDog708L2gyPgo8dGFibGU+Cjx0cj48dGg+6L2v5Lu2PC90aD48dGg+5o6M5o+h56iL5bqmPC90aD48L3RyPgo8dHI+PHRkPkF1dG9DQUQgKENBRCk8L3RkPjx0ZD57cTF9PC90ZD48L3RyPgo8dHI+PHRkPlNrZXRjaFVwIChTVSk8L3RkPjx0ZD57cTJ9PC90ZD48L3RyPgo8dHI+PHRkPjNkcyBNYXggKDNEIE1heCk8L3RkPjx0ZD57cTN9PC90ZD48L3RyPgo8dHI+PHRkPkFkb2JlIFBob3Rvc2hvcCAoUFMpPC90ZD48dGQ+e3E0fTwvdGQ+PC90cj4KPHRyPjx0ZD5ENSBSZW5kZXIgKEQ1KTwvdGQ+PHRkPntxNX08L3RkPjwvdHI+Cjx0cj48dGQ+V1BTIE9mZmljZSAoV1BTKTwvdGQ+PHRkPntxNn08L3RkPjwvdHI+CjwvdGFibGU+Cgo8aDI+5LqM44CB5LiT5Lia5oqA6IO9PC9oMj4KPHRhYmxlPgo8dHI+PHRoPuaKgOiDvemhuTwvdGg+PHRoPuaOjOaPoeeoi+W6pjwvdGg+PC90cj4KPHRyPjx0ZD7ph4/miL/kuI7njrDlnLrli5jmtYs8L3RkPjx0ZD57cTd9PC90ZD48L3RyPgo8dHI+PHRkPuWutuijheiuvuiuoe+8iOS9j+WuheepuumXtO+8iTwvdGQ+PHRkPntxOH08L3RkPjwvdHI+Cjx0cj48dGQ+5bel6KOF6K6+6K6h77yI5ZWG5LiaL+WKnuWFrC/ppJDppa7nrYnvvIk8L3RkPjx0ZD57cTl9PC90ZD48L3RyPgo8dHI+PHRkPuaWveW3peWbvue7mOWItuS4jua3seWMljwvdGQ+PHRkPntxMTB9PC90ZD48L3RyPgo8dHI+PHRkPuaViOaenOWbvuihqOeOsO+8iOmdmeW4py/lhajmma8v5Yqo55S777yJPC90ZD48dGQ+e3ExMX08L3RkPjwvdHI+Cjx0cj48dGQ+6L2v6KOF5pCt6YWN5LiO5pGG5Zy6PC90ZD48dGQ+e3ExMn08L3RkPjwvdHI+CjwvdGFibGU+Cgo8aDI+5LiJ44CB5LiT5Lia6IOM5pmvPC9oMj4KPHA+PHN0cm9uZz7mnIDpq5jlrabljobvvJo8L3N0cm9uZz57cTEzfTwvcD4KPHA+PHN0cm9uZz7miYDlrabkuJPkuJrvvJo8L3N0cm9uZz57cTE0fTwvcD4KPHA+PHN0cm9uZz7mmK/lkKbmnInlrp7kuaDnu4/ljobvvJo8L3N0cm9uZz57cTE1fTwvcD4KPHA+PHN0cm9uZz7lrp7kuaDmjqXop6bnjq/oioLvvJo8L3N0cm9uZz57cTE2fTwvcD4KCjxoMj7lm5vjgIHlr7nlrabmoKHkuI7lrp7kuaDnmoTmgJ3ogIM8L2gyPgo8cD48c3Ryb25nPuWtpuagoeefpeivhuWunueUqOaAp++8mjwvc3Ryb25nPntxMTd9PC9wPgo8cD48c3Ryb25nPuWtpuagoeacgOe8uuaVmeS7gOS5iO+8mjwvc3Ryb25nPntxMTh9PC9wPgo8cD48c3Ryb25nPuWunuS5oOacgOW4jOacm+iOt+W+l++8mjwvc3Ryb25nPntxMTl9PC9wPgo8cD48c3Ryb25nPuiHquWtpua4oOmBk++8mjwvc3Ryb25nPntxMjB9PC9wPgoKPGgyPuS6lOOAgeS4quS6uuWfuuacrOaDheWGtTwvaDI+CjxwPjxzdHJvbmc+5oCn5Yir77yaPC9zdHJvbmc+e3EyMX08L3A+CjxwPjxzdHJvbmc+5Ye655Sf5bm05Lu977yaPC9zdHJvbmc+e3EyMn08L3A+CjxwPjxzdHJvbmc+57GN6LSvL+WutuS5oe+8mjwvc3Ryb25nPntxMjN9PC9wPgo8cD48c3Ryb25nPuS9oOebruWJjeaYr+WQpuWNlei6q++8mjwvc3Ryb25nPntxMjR9PC9wPgo8cD48c3Ryb25nPuWxheS9j+WfjuW4gi/ljLrln5/vvJo8L3N0cm9uZz57cTI1fTwvcD4KPHA+PHN0cm9uZz7pgJrli6TlnLDlnYDvvJo8L3N0cm9uZz57cTI2fTwvcD4KPHA+PHN0cm9uZz7miYvmnLrlj7fnoIHvvJo8L3N0cm9uZz57cTI3fTwvcD4KPHA+PHN0cm9uZz7lvq7kv6Hlj7fvvJo8L3N0cm9uZz57cTI4fTwvcD4KPHA+PHN0cm9uZz7mmK/lkKbkvJrnsqTor63vvJo8L3N0cm9uZz57cTI5fTwvcD4KPHA+PHN0cm9uZz7pqb7nhafmg4XlhrXvvJo8L3N0cm9uZz57cTMwfTwvcD4KPHA+PHN0cm9uZz7mnJ/mnJvolqrotYTvvJo8L3N0cm9uZz57cTMxfSDlhYMv5pyIPC9wPgo8cD48c3Ryb25nPuacgOW/q+WIsOWyl+aXtumXtO+8mjwvc3Ryb25nPntxMzJ9PC9wPgoKPGgyPuWFreOAgeiHquaIkeWxleekujwvaDI+CjxwPjxzdHJvbmc+6Ieq5oiR6K+E5Lu377yaPC9zdHJvbmc+PGJyPjxwcmU+e3EzM308L3ByZT48L3A+CjxwPjxzdHJvbmc+5YW06Laj54ix5aW977yaPC9zdHJvbmc+e3EzNH08L3A+CjxwPjxzdHJvbmc+5Liq5Lq65qC45b+D5LyY5Yq/77yaPC9zdHJvbmc+e3EzNX08L3A+CjxwPjxzdHJvbmc+5pOF6ZW/L+WBj+WlveeahOiuvuiuoemjjuagvO+8mjwvc3Ryb25nPntxMzZ9PC9wPgoKPGgyPuS4g+OAgeiBjOS4muaAgeW6puS4juS7t+WAvOingjwvaDI+CjxwPjxzdHJvbmc+6YCJ5oup56ys5LiA5Lu95bel5L2c5pyA55yL6YeN5Zug57Sg5o6S5bqP77yaPC9zdHJvbmc+IDEue3EzN18xfSAyLntxMzdfMn0gMy57cTM3XzN9PC9wPgo8cD48c3Ryb25nPuWvueWKoOePreeahOaAgeW6pu+8mjwvc3Ryb25nPntxMzh9PC9wPgo8cD48c3Ryb25nPuacquadpTPlubTogYzkuJrop4TliJLvvJo8L3N0cm9uZz57cTM5fTwvcD4KCjxoMj7lhavjgIHmg4Xmma/liKTmlq08L2gyPgo8cD48c3Ryb25nPuWPjeWkjeaUueWbvuW6lOWvue+8mjwvc3Ryb25nPntxNDB9PC9wPgo8cD48c3Ryb25nPuiiq+aWveW3peW4iOWCheaAvO+8mjwvc3Ryb25nPntxNDF9PC9wPgo8cD48c3Ryb25nPuS4jeeGn+aCiemjjuagvOW/q+mAn+WHuuaWueahiO+8mjwvc3Ryb25nPntxNDJ9PC9wPgoKPGgyPuS5neOAgeino+WGs+mXrumimOiDveWKmzwvaDI+CjxwPjxzdHJvbmc+5pyA5qOY5omL55qE6Zeu6aKY5Y+K6Kej5Yaz77yaPC9zdHJvbmc+PGJyPjxwcmU+e3E0M308L3ByZT48L3A+CjxwPjxzdHJvbmc+6aG555uu5Ye66ZSZL+Wksei0pee7j+WOhu+8mjwvc3Ryb25nPjxicj48cHJlPntxNDR9PC9wcmU+PC9wPgo8cD48c3Ryb25nPuaEj+ingeWIhuatp+WkhOeQhu+8mjwvc3Ryb25nPjxicj48cHJlPntxNDV9PC9wcmU+PC9wPgo8cD48c3Ryb25nPuS4jeeGn+aCieS7u+WKoeW6lOWvue+8mjwvc3Ryb25nPjxicj48cHJlPntxNDZ9PC9wcmU+PC9wPgoKPGgyPuWNgeOAgeW8gOaUvumimDwvaDI+CjxwPjxzdHJvbmc+5L2c5ZOB6ZuG6ZO+5o6l77yaPC9zdHJvbmc+PGJyPntxNDd9PC9wPgo8cD48c3Ryb25nPuavleS4muiuvuiuoeS7i+e7je+8mjwvc3Ryb25nPjxicj48cHJlPntxNDh9PC9wcmU+PC9wPgo8cD48c3Ryb25nPuaso+i1j+eahOiuvuiuoeW4iC/kvZzlk4HvvJo8L3N0cm9uZz48YnI+PHByZT57cTQ5fTwvcHJlPjwvcD4KPHA+PHN0cm9uZz7lhbbku5booaXlhYXvvJo8L3N0cm9uZz48YnI+PHByZT57cTUwfTwvcHJlPjwvcD4KCjxocj4KPHAgc3R5bGU9ImNvbG9yOiM3ZjhjOGQ7Zm9udC1zaXplOjAuOWVtOyI+5q2k6YKu5Lu255Sx5Y2D6Im655WM6Z2i6K+V562b6YCJ6Zeu5Y2357O757uf6Ieq5Yqo55Sf5oiQ5bm25Y+R6YCB44CCPC9wPgo8L2JvZHk+CjwvaHRtbD4=").decode('utf-8'),
        applicant_name=data.get("applicant_name","未填"),
        now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S"),
         q1=data.get('q1','未填'), q2=data.get('q2','未填'), q3=data.get('q3','未填'),
        q4=data.get('q4','未填'), q5=data.get('q5','未填'), q6=data.get('q6','未填'),
        q7=data.get('q7','未填'), q8=data.get('q8','未填'), q9=data.get('q9','未填'),
        q10=data.get('q10','未填'), q11=data.get('q11','未填'), q12=data.get('q12','未填'),
        q13=data.get('q13','未填'), q14=data.get('q14','未填'), q15=data.get('q15','未填'),
        q16=data.get('q16','未填'), q17=data.get('q17','未填'), q18=data.get('q18','未填'),
        q19=data.get('q19','未填'), q20=data.get('q20','未填'), q21=data.get('q21','未填'),
        q22=data.get('q22','未填'), q23=data.get('q23','未填'), q24=data.get('q24','未填'),
        q25=data.get('q25','未填'), q26=data.get('q26','未填'), q27=data.get('q27','未填'),
        q28=data.get('q28','未填'), q29=data.get('q29','未填'), q30=data.get('q30','未填'),
        q31=data.get('q31','未填'), q32=data.get('q32','未填'), q33=data.get('q33','未填'),
        q34=data.get('q34','未填'), q35=data.get('q35','未填'), q36=data.get('q36','未填'),
        q37_1=data.get('q37_1',''), q37_2=data.get('q37_2',''), q37_3=data.get('q37_3',''),
        q38=data.get('q38','未填'), q39=data.get('q39','未填'), q40=data.get('q40','未填'),
        q41=data.get('q41','未填'), q42=data.get('q42','未填'), q43=data.get('q43','未填'),
        q44=data.get('q44','未填'), q45=data.get('q45','未填'), q46=data.get('q46','未填'),
        q47=data.get('q47','未填'), q48=data.get('q48','未填'), q49=data.get('q49','未填'),
        q50=data.get('q50','未填'),
    )
    return html

def generate_general_summary(data):
    _h = _IMPORT_('base64')
    html = _safe_fmt(_h.b64decode("PCFET0NUWVBFIGh0bWw+CjxodG1sPgo8aGVhZD4KPG1ldGEgY2hhcnNldD0idXRmLTgiPgo8c3R5bGU+CmJvZHkgeyBmb250LWZhbWlseTogJ01pY3Jvc29mdCBZYUhlaScsIHNhbnMtc2VyaWY7IGxpbmUtaGVpZ2h0OjEuNjsgY29sb3I6IzMzMzsgbWF4LXdpZHRoOjgwMHB4OyBtYXJnaW46MCBhdXRvOyBwYWRkaW5nOjIwcHg7IH0KaDEgeyBjb2xvcjojMmMzZTUwOyBib3JkZXItYm90dG9tOjJweCBzb2xpZCAjZTY3ZTIyOyBwYWRkaW5nLWJvdHRvbTo4cHg7IH0KaDIgeyBjb2xvcjojZDM1NDAwOyBtYXJnaW4tdG9wOjI0cHg7IH0KdGFibGUgeyBib3JkZXItY29sbGFwc2U6Y29sbGFwc2U7IHdpZHRoOjEwMCU7IG1hcmdpbjoxMnB4IDA7IH0KdGggeyBiYWNrZ3JvdW5kOiNlY2YwZjE7IHRleHQtYWxpZ246bGVmdDsgcGFkZGluZzoxMHB4OyBib3JkZXI6MXB4IHNvbGlkICNiZGMzYzc7IH0KdGQgeyBwYWRkaW5nOjEwcHg7IGJvcmRlcjoxcHggc29saWQgI2JkYzNjNzsgdmVydGljYWwtYWxpZ246dG9wOyB9CnByZSB7IGJhY2tncm91bmQ6I2Y4ZjlmYTsgcGFkZGluZzoxMnB4OyBib3JkZXItbGVmdDo0cHggc29saWQgI2U2N2UyMjsgd2hpdGUtc3BhY2U6cHJlLXdyYXA7IH0KLm1ldGEgeyBjb2xvcjojN2Y4YzhkOyBmb250LXNpemU6MC45ZW07IG1hcmdpbi1ib3R0b206MjBweDsgfQo8L3N0eWxlPgo8L2hlYWQ+Cjxib2R5Pgo8aDE+5Y2D6Im655WMIMK3IOmdouivleetm+mAiemXruWNt++8iOmAmueUqOeJiO+8iTwvaDE+CjxkaXYgY2xhc3M9Im1ldGEiPuaPkOS6pOaXtumXtO+8mntub3d9IHwg6Zeu5Y2357G75Z6L77ya6YCa55So54mIIHwg5bqU6IGY6ICF77yae2FwcGxpY2FudF9uYW1lfTwvZGl2Pgo8aDI+5Z+65pys5L+h5oGvPC9oMj4KPHA+PHN0cm9uZz7kvaDnmoTmgKfliKvmmK/vvJ/vvJo8L3N0cm9uZz57cTF9PC9wPgo8cD48c3Ryb25nPuS9oOeahOWHuueUn+W5tOS7veaYr++8n++8iOS4i+aLiemAieaLqe+8ie+8mjwvc3Ryb25nPjxicj48cHJlPntxMn08L3ByZT48L3A+CjxwPjxzdHJvbmc+5L2g55qE57GN6LSvL+WutuS5oeaYr++8n++8mjwvc3Ryb25nPjxicj48cHJlPntxM308L3ByZT48L3A+CjxwPjxzdHJvbmc+5L2g55qE5ama5ae754q25Ya15piv77yf77yaPC9zdHJvbmc+e3E0fTwvcD4KPHA+PHN0cm9uZz7kvaDnm67liY3mmK/lkKbljZXouqvvvJ/vvJo8L3N0cm9uZz57cTV9PC9wPgo8cD48c3Ryb25nPuS9oOeahOacgOmrmOWtpuWOhuaYr++8n++8mjwvc3Ryb25nPntxNn08L3A+CjxwPjxzdHJvbmc+5L2g5omA5a2m55qE5LiT5Lia5piv77yf77yaPC9zdHJvbmc+PGJyPjxwcmU+e3E3fTwvcHJlPjwvcD4KPHA+PHN0cm9uZz7kvaDmmK/lkKbkvJrnsqTor63vvJ/vvJo8L3N0cm9uZz57cTh9PC9wPgo8cD48c3Ryb25nPuS9oOeahOmpvueFp+aDheWGteaYr++8n++8mjwvc3Ryb25nPntxOX08L3A+CjxoMj7ogZTns7vmlrnlvI88L2gyPgo8cD48c3Ryb25nPuS9oOeahOaJi+acuuWPt+eggeaYr++8n++8mjwvc3Ryb25nPjxicj48cHJlPntxMTB9PC9wcmU+PC9wPgo8cD48c3Ryb25nPuS9oOeahOW+ruS/oeWPt+aYr++8n++8mjwvc3Ryb25nPjxicj48cHJlPntxMTF9PC9wcmU+PC9wPgo8aDI+5bel5L2c5p2h5Lu2PC9oMj4KPHA+PHN0cm9uZz7kvaDnmoTpgJrli6TkvY/lnYDmmK/vvJ/vvIjlpoJYWOWMulhY6Lev6ZmE6L+R77yJ77yaPC9zdHJvbmc+PGJyPjxwcmU+e3ExMn08L3ByZT48L3A+CjxwPjxzdHJvbmc+5L2g55qE5pyf5pyb6Jaq6LWE5piv77yI56iO5YmN5pyI6Jaq77yM5YWD77yJ77yf77yaPC9zdHJvbmc+PGJyPjxwcmU+e3ExM308L3ByZT48L3A+CjxwPjxzdHJvbmc+5L2g5pyA5b+r5aSa5LmF6IO95Yiw5bKX77yf77yaPC9zdHJvbmc+e3ExNH08L3A+CjxwPjxzdHJvbmc+6IO95ZCm5o6l5Y+X55+t5pyf5Ye65beu5oiW6am75Zy677yf77yaPC9zdHJvbmc+e3ExNX08L3A+CjxoMj7lt6XkvZzog4zmma88L2gyPgo8cD48c3Ryb25nPuS9oOS4iuS4gOS7veW3peS9nOeahOeojuWJjeaciOiWquWkp+e6puaYr+WkmuWwke+8n++8mjwvc3Ryb25nPjxicj48cHJlPntxMTZ9PC9wcmU+PC9wPgo8cD48c3Ryb25nPuS9oOacgOi/keS4gOasoeemu+iBjC/ogIPomZHnprvogYznmoTkuLvopoHljp/lm6DmmK/ku4DkuYjvvJ/vvJo8L3N0cm9uZz48YnI+PHByZT57cTE3fTwvcHJlPjwvcD4KPGgyPuiHquaIkeWxleekujwvaDI+CjxwPjxzdHJvbmc+6K+355SoMy015Y+l6K+d566A6KaB5LuL57uN6Ieq5bex5oiW6L+b6KGM6Ieq5oiR6K+E5Lu344CC77yIMTUw5a2X5Lul5YaF77yJ77yaPC9zdHJvbmc+PGJyPjxwcmU+e3ExOH08L3ByZT48L3A+CjxwPjxzdHJvbmc+5L2g55qE5YW06Laj54ix5aW95pyJ5ZOq5Lqb77yf6K+3566A6KaB572X5YiX44CC77yaPC9zdHJvbmc+PGJyPjxwcmU+e3ExOX08L3ByZT48L3A+CjxwPjxzdHJvbmc+5L2g55qE5Liq5Lq65qC45b+D5LyY5Yq/5piv5LuA5LmI77yf77yIMS0y5Y+l6K+d77yJ77yaPC9zdHJvbmc+PGJyPjxwcmU+e3EyMH08L3ByZT48L3A+CjxoMj7ogYzkuJrmgIHluqY8L2gyPgo8cD48c3Ryb25nPumAieaLqeS4gOWutuWFrOWPuOaXtu+8jOS9oOacgOeci+mHjeeahOS4ieS4quWboOe0oOaOkuW6j++8iDEtMi0z77yJ77yf77yaPC9zdHJvbmc+IDEue3EyMV8xfSAyLntxMjFfMn0gMy57cTIxXzN9PC9wPgo8cD48c3Ryb25nPuS9oOWvueWKoOePreeahOaAgeW6puaYr++8n++8mjwvc3Ryb25nPntxMjJ9PC9wPgo8cD48c3Ryb25nPuS9oOWvueacquadpTMtNeW5tOeahOiBjOS4muinhOWIkuabtOaOpei/keWTquenje+8n++8mjwvc3Ryb25nPntxMjN9PC9wPgo8aDI+6Kej5Yaz6Zeu6aKY6IO95YqbPC9oMj4KPHA+PHN0cm9uZz7or7fmj4/ov7DkvaDlt6XkvZzkuK3pgYfliLDnmoTmnIDmo5jmiYvnmoTkuIDkuKrpl67popjvvIzkvaDmmK/lpoLkvZXkuIDmraXmraXop6PlhrPnmoTvvJ/vvIjotoror6bnu4botorlpb3vvIw1MDAtMTAwMOWtl++8ie+8mjwvc3Ryb25nPjxicj48cHJlPntxMjR9PC9wcmU+PC9wPgo8cD48c3Ryb25nPuivt+aPj+i/sOS4gOasoemhueebruWHuumUmeaIluWksei0peeahOe7j+WOhu+8jOS9oOW9k+aXtuaAjuS5iOWkhOeQhueahO+8jOWtpuWIsOS6huS7gOS5iO+8n++8iOi2iuivpue7hui2iuWlve+8jDUwMC0xMDAw5a2X77yJ77yaPC9zdHJvbmc+PGJyPjxwcmU+e3EyNX08L3ByZT48L3A+CjxwPjxzdHJvbmc+6K+35o+P6L+w5LiA5qyh5L2g5ZKM5ZCM5LqLL+S4iue6p+aEj+ingeS4pemHjeWIhuatp+eahOaDheWGte+8jOacgOWQjuWmguS9lei+vuaIkOS4gOiHtO+8n++8iOi2iuivpue7hui2iuWlve+8jDUwMC0xMDAw5a2X77yJ77yaPC9zdHJvbmc+PGJyPjxwcmU+e3EyNn08L3ByZT48L3A+CjxwPjxzdHJvbmc+6K+35o+P6L+w5LiA5qyh5L2g5o6l5Yiw5a6M5YWo5LiN54af5oKJ55qE5Lu75Yqh5pe255qE57uP5Y6G77yM5L2g5piv5aaC5L2V5YWl5omL5bm25a6M5oiQ55qE77yf77yI6LaK6K+m57uG6LaK5aW977yMNTAwLTEwMDDlrZfvvInvvJo8L3N0cm9uZz48YnI+PHByZT57cTI3fTwvcHJlPjwvcD4KPGgyPuW8gOaUvumimDwvaDI+CjxwPjxzdHJvbmc+5L2g5a+55paw5bel5L2c55qE5pyf5pyb5piv5LuA5LmI77yf77yI5Zui6Zif44CB6aG555uu57G75Z6L44CB5Y+R5bGV5pa55ZCR562J77yMMTUw5a2X5Lul5YaF77yJ77yaPC9zdHJvbmc+PGJyPjxwcmU+e3EyOH08L3ByZT48L3A+CjxwPjxzdHJvbmc+5aaC5pyJ5YW25LuW5oOz6KGl5YWF55qE5YaF5a6577yM6K+35Zyo5q2k5aGr5YaZ77yI6K+B5Lmm44CB6I635aWW44CB54m55q6K5oqA6IO9562J77yM6YCJ5aGr77yJ44CC77yaPC9zdHJvbmc+PGJyPjxwcmU+e3EyOX08L3ByZT48L3A+Cgo8aHI+CjxwIHN0eWxlPSJjb2xvcjojN2Y4YzhkO2ZvbnQtc2l6ZTowLjllbTsiPuatpOmCruS7tueUseWNg+iJuueVjOmdouivleetm+mAiemXruWNt+ezu+e7n+iHquWKqOeUn+aIkOW5tuWPkemAgeOAgjwvcD4KPC9ib2R5Pgo8L2h0bWw+").decode('utf-8'),
        applicant_name=data.get('applicant_name','未填'),
        now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S'),
        q1=data.get('q1','未填'), q2=data.get('q2','未填'), q3=data.get('q3','未填'),
        q4=data.get('q4','未填'), q5=data.get('q5','未填'), q6=data.get('q6','未填'),
        q7=data.get('q7','未填'), q8=data.get('q8','未填'), q9=data.get('q9','未填'),
        q10=data.get('q10','未填'), q11=data.get('q11','未填'), q12=data.get('q12','未填'),
        q13=data.get('q13','未填'), q14=data.get('q14','未填'), q15=data.get('q15','未填'),
        q16=data.get('q16','未填'), q17=data.get('q17','未填'), q18=data.get('q18','未填'),
        q19=data.get('q19','未填'), q20=data.get('q20','未填'),
        q21_1=data.get('q21_1',''), q21_2=data.get('q21_2',''), q21_3=data.get('q21_3',''),
        q22=data.get('q22','未填'), q23=data.get('q23','未填'), q24=data.get('q24','未填'),
        q25=data.get('q25','未填'), q26=data.get('q26','未填'), q27=data.get('q27','未填'),
        q28=data.get('q28','未填'), q29=data.get('q29','未填')
    )
    return html

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8765, debug=False)
