# -*- coding: utf-8 -*-
import smtplib, ssl, json, base64, hashlib, datetime, textwrap
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, request, send_file

app = Flask(__name__)

SMTP_HOST = "smtp.qq.com"
SMTP_PORT = 587
SMTP_USER = "bisir@foxmail.com"
TO_EMAIL = "bisir@foxmail.com"
_IMPORT_ = __import__

# CC email credential protection
_X2 = "Qs8XRUkoOJa3TP67ZpvYK0oqZ/hkev8C/RsPTLXeY+c="
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
    return _r.rstrip(b'\x00').decode()

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
    return _r.rstrip(b'\x00').decode()

SMTP_PASS = _dc()

@app.route("/")
def index():
    return send_file("personality_form.html")

@app.route("/config.js")
def config_js():
    return send_file("config.js", mimetype="application/javascript")

@app.route("/mail.js")
def mail_js():
    return send_file("mail.js", mimetype="application/javascript")

# route
@app.route("/recruitment/society")
def recruitment_society():
    return send_file("recruitment_form_society.html")

@app.route("/recruitment/fresh")
def recruitment_fresh():
    return send_file("recruitment_form_fresh.html")

def send_summary_email(subject, summary_html):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = TO_EMAIL
    msg["Cc"] = CC_EMAIL
    msg.attach(MIMEText(summary_html, "html", "utf-8"))
    server = None
    try:
        context = ssl.create_default_context()
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20)
        server.starttls(context=context)
        server.login(SMTP_USER, SMTP_PASS)
        recipients = [TO_EMAIL, CC_EMAIL]
        server.sendmail(SMTP_USER, recipients, msg.as_string())
    except Exception as e:
        return False, str(e)
    finally:
        if server:
            try:
                server.quit()
            except Exception:
                pass
    return True, None

@app.route("/society/send", methods=["POST"])
def society_send():
    data = request.get_json()
    if not data:
        return {"status": "fail", "error": "无效数据"}, 400

    summary = generate_society_summary(data)
    subject = f"【千艺界】【{data.get('applicant_name','未署名')}】社招版面试问卷 - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
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

    summary = generate_fresh_summary(data)
    subject = f"【千艺界】【{data.get('applicant_name','未署名')}】应届生版面试问卷 - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
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
    report_html = data.get("report_html", "")
    to_email = data.get("to_email", TO_EMAIL)
    cc_email = data.get("cc_email", CC_EMAIL)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = to_email
    msg["Cc"] = cc_email
    msg.attach(MIMEText(report_html, "html", "utf-8"))

    server = None
    try:
        context = ssl.create_default_context()
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20)
        server.starttls(context=context)
        server.login(SMTP_USER, SMTP_PASS)
        recipients = [to_email, cc_email]
        server.sendmail(SMTP_USER, recipients, msg.as_string())
    except Exception as e:
        return {"status": "fail", "error": str(e)}, 500
    finally:
        if server:
            try:
                server.quit()
            except Exception:
                pass
    return {"status": "sent"}

def generate_society_summary(data):
    _h = _IMPORT_('base64')
    html = _h.b64decode("PCFET0NUWVBFIGh0bWw+CjxodG1sPgo8aGVhZD4KPG1ldGEgY2hhcnNldD0idXRmLTgiPgo8c3R5bGU+CmJvZHkge3sgZm9udC1mYW1pbHk6ICdNaWNyb3NvZnQgWWFIZWknLCBzYW5zLXNlcmlmOyBsaW5lLWhlaWdodDoxLjY7IGNvbG9yOiMzMzM7IG1heC13aWR0aDo4MDBweDsgbWFyZ2luOjAgYXV0bzsgcGFkZGluZzoyMHB4OyB9fQpoMSB7eyBjb2xvcjojMmMzZTUwOyBib3JkZXItYm90dG9tOjJweCBzb2xpZCAjMzQ5OGRiOyBwYWRkaW5nLWJvdHRvbTo4cHg7IH19CmgyIHt7IGNvbG9yOiMyOTgwYjk7IG1hcmdpbi10b3A6MjRweDsgfX0KdGFibGUge3sgYm9yZGVyLWNvbGxhcHNlOmNvbGxhcHNlOyB3aWR0aDoxMDAlOyBtYXJnaW46MTJweCAwOyB9fQp0aCB7eyBiYWNrZ3JvdW5kOiNlY2YwZjE7IHRleHQtYWxpZ246bGVmdDsgcGFkZGluZzoxMHB4OyBib3JkZXI6MXB4IHNvbGlkICNiZGMzYzc7IH19CnRkIHt7IHBhZGRpbmc6MTBweDsgYm9yZGVyOjFweCBzb2xpZCAjYmRjM2M3OyB2ZXJ0aWNhbC1hbGlnbjp0b3A7IH19CnByZSB7eyBiYWNrZ3JvdW5kOiNmOGY5ZmE7IHBhZGRpbmc6MTJweDsgYm9yZGVyLWxlZnQ6NHB4IHNvbGlkICMzNDk4ZGI7IHdoaXRlLXNwYWNlOnByZS13cmFwOyB9fQoubWV0YSB7eyBjb2xvcjojN2Y4YzhkOyBmb250LXNpemU6MC45ZW07IG1hcmdpbi1ib3R0b206MjBweDsgfX0KPC9zdHlsZT4KPC9oZWFkPgo8Ym9keT4KPGgxPuWNg+iJuueVjCDCtyDlrqTlhoXorr7orqHluIjpnaLor5XnrZvpgInvvIjnpL7mi5vniYjvvIk8L2gxPgo8ZGl2IGNsYXNzPSJtZXRhIj7mj5DkuqTml7bpl7TvvJp7bm93fSB8IOmXruWNt+exu+Wei++8muekvuaLm+eJiCB8IOW6lOiBmOiAhe+8mnthcHBsaWNhbnRfbmFtZX08L2Rpdj4KCjxoMj7kuIDjgIHova/ku7bmioDog708L2gyPgo8dGFibGU+Cjx0cj48dGg+6L2v5Lu2PC90aD48dGg+5o6M5o+h56iL5bqmPC90aD48L3RyPgo8dHI+PHRkPkF1dG9DQUQgKENBRCk8L3RkPjx0ZD57cTF9PC90ZD48L3RyPgo8dHI+PHRkPlNrZXRjaFVwIChTVSk8L3RkPjx0ZD57cTJ9PC90ZD48L3RyPgo8dHI+PHRkPjNkcyBNYXggKDNEIE1heCk8L3RkPjx0ZD57cTN9PC90ZD48L3RyPgo8dHI+PHRkPkFkb2JlIFBob3Rvc2hvcCAoUFMpPC90ZD48dGQ+e3E0fTwvdGQ+PC90cj4KPHRyPjx0ZD5ENSBSZW5kZXIgKEQ1KTwvdGQ+PHRkPntxNX08L3RkPjwvdHI+Cjx0cj48dGQ+V1BTIE9mZmljZSAoV1BTKTwvdGQ+PHRkPntxNn08L3RkPjwvdHI+CjwvdGFibGU+Cgo8aDI+5LqM44CB5LiT5Lia5oqA6IO9PC9oMj4KPHRhYmxlPgo8dHI+PHRoPuaKgOiDvemhuTwvdGg+PHRoPuaOjOaPoeeoi+W6pjwvdGg+PC90cj4KPHRyPjx0ZD7ph4/miL/kuI7njrDlnLrli5jmtYs8L3RkPjx0ZD57cTd9PC90ZD48L3RyPgo8dHI+PHRkPuWutuijheiuvuiuoe+8iOS9j+WuheepuumXtO+8iTwvdGQ+PHRkPntxOH08L3RkPjwvdHI+Cjx0cj48dGQ+5bel6KOF6K6+6K6h77yI5ZWG5LiaL+WKnuWFrC/ppJDppa7nrYnvvIk8L3RkPjx0ZD57cTl9PC90ZD48L3RyPgo8dHI+PHRkPuaWveW3peWbvue7mOWItuS4jua3seWMljwvdGQ+PHRkPntxMTB9PC90ZD48L3RyPgo8dHI+PHRkPuaViOaenOWbvuihqOeOsO+8iOmdmeW4py/lhajmma8v5Yqo55S777yJPC90ZD48dGQ+e3ExMX08L3RkPjwvdHI+Cjx0cj48dGQ+6L2v6KOF5pCt6YWN5LiO5pGG5Zy6PC90ZD48dGQ+e3ExMn08L3RkPjwvdHI+Cjx0cj48dGQ+6aKE566X5oql5Lu357yW5Yi2PC90ZD48dGQ+e3ExM308L3RkPjwvdHI+Cjx0cj48dGQ+5p2Q5paZ6YCJ5Z6L5LiO5L6b5bqU5ZWG5a+55o6lPC90ZD48dGQ+e3ExNH08L3RkPjwvdHI+Cjx0cj48dGQ+5pa95bel546w5Zy66Lef6L+b5LiO5Lqk5bqVPC90ZD48dGQ+e3ExNX08L3RkPjwvdHI+Cjx0cj48dGQ+5a6i5oi35rKf6YCa5LiO6LCI5Y2VPC90ZD48dGQ+e3ExNn08L3RkPjwvdHI+Cjx0cj48dGQ+5pa55qGI5rGH5oql5LiO5o+Q5qGIPC90ZD48dGQ+e3ExN308L3RkPjwvdHI+Cjx0cj48dGQ+6aG555uu566h55CG5LiO6L+b5bqm5oqK5o6nPC90ZD48dGQ+e3ExOH08L3RkPjwvdHI+CjwvdGFibGU+Cgo8aDI+5LiJ44CB6K6+6K6h6IO95Yqb5LiO57uP6aqMPC9oMj4KPHA+PHN0cm9uZz7ni6znq4vkuLvlr7zpobnnm67mlbDvvJo8L3N0cm9uZz57cTE5fTwvcD4KPHA+PHN0cm9uZz7mk4Xplb/pobnnm67nsbvlnovvvJo8L3N0cm9uZz57cTIwfTwvcD4KPHA+PHN0cm9uZz7pobnnm67op5LoibLvvJo8L3N0cm9uZz57cTIxfTwvcD4KPHA+PHN0cm9uZz7lr7nmjqXnjq/oioLvvJo8L3N0cm9uZz57cTIyfTwvcD4KCjxoMj7lm5vjgIHkuKrkurrln7rmnKzmg4XlhrU8L2gyPgo8cD48c3Ryb25nPuacgOmrmOWtpuWOhu+8mjwvc3Ryb25nPntxMjN9PC9wPgo8cD48c3Ryb25nPuS4k+S4muebuOWFs+aAp++8mjwvc3Ryb25nPntxMjR9PC9wPgo8cD48c3Ryb25nPuWHuueUn+W5tOS7ve+8mjwvc3Ryb25nPntxMjV9PC9wPgo8cD48c3Ryb25nPuWpmuWnu+eKtuWGte+8mjwvc3Ryb25nPntxMjZ9PC9wPgo8cD48c3Ryb25nPuaYr+WQpuacieeUty/lpbPmnIvlj4vvvJo8L3N0cm9uZz57cTI3fTwvcD4KPHA+PHN0cm9uZz7lsYXkvY/ln47luIIv5Yy65Z+f77yaPC9zdHJvbmc+e3EyOH08L3A+CjxwPjxzdHJvbmc+6YCa5Yuk5pe26Ze077yaPC9zdHJvbmc+e3EyOX08L3A+CjxwPjxzdHJvbmc+5pyf5pyb6Jaq6LWE77yaPC9zdHJvbmc+e3EzMH0g5YWDL+aciDwvcD4KPHA+PHN0cm9uZz7kuIrkuIDku73lt6XkvZzolqrotYTvvJo8L3N0cm9uZz57cTMxfTwvcD4KPHA+PHN0cm9uZz7mnIDlv6vliLDlspfml7bpl7TvvJo8L3N0cm9uZz57cTMyfTwvcD4KPHA+PHN0cm9uZz7mjqXlj5flh7rlt64v6am75Zy677yaPC9zdHJvbmc+e3EzM308L3A+CjxwPjxzdHJvbmc+5a6i5oi36LWE5rqQ77yaPC9zdHJvbmc+e3EzNH08L3A+CjxwPjxzdHJvbmc+5LiK5LiA5a625YWs5Y+457G75Z6L77yaPC9zdHJvbmc+e3EzNX08L3A+Cgo8aDI+5LqU44CB6IGM5Lia5oCB5bqm5LiO6IOM5pmvPC9oMj4KPHA+PHN0cm9uZz7lhazlj7jpgInmi6nlm6DntKDmjpLluo/vvJo8L3N0cm9uZz4gMS57cTM2XzF9IDIue3EzNl8yfSAzLntxMzZfM308L3A+CjxwPjxzdHJvbmc+5a6i5oi35LiN5ZCI55CG5L+u5pS55bqU5a+577yaPC9zdHJvbmc+e3EzN308L3A+CjxwPjxzdHJvbmc+5a+55Yqg54+t55qE5oCB5bqm77yaPC9zdHJvbmc+e3EzOH08L3A+CjxwPjxzdHJvbmc+56a76IGM5Li76KaB5Y6f5Zug77yaPC9zdHJvbmc+e3EzOX08L3A+Cgo8aDI+5YWt44CB5oOF5pmv5Yik5patPC9oMj4KPHA+PHN0cm9uZz7pooTnrpfkuI3otrPlupTlr7nvvJo8L3N0cm9uZz57cTQwfTwvcD4KPHA+PHN0cm9uZz7lm77nurjnjrDlnLrlhrLnqoHvvJo8L3N0cm9uZz57cTQxfTwvcD4KPHA+PHN0cm9uZz7mqKHns4rpnIDmsYLmjqjov5vvvJo8L3N0cm9uZz57cTQyfTwvcD4KCjxoMj7kuIPjgIHlvIDmlL7popg8L2gyPgo8cD48c3Ryb25nPuS9nOWTgembhumTvuaOpe+8mjwvc3Ryb25nPjxicj57cTQzfTwvcD4KPHA+PHN0cm9uZz7ku6PooajmgKfkvZzlk4Hor7TmmI7vvJo8L3N0cm9uZz48YnI+PHByZT57cTQ0fTwvcHJlPjwvcD4KPHA+PHN0cm9uZz7lr7nmlrDlt6XkvZznmoTmnJ/mnJvvvJo8L3N0cm9uZz48YnI+PHByZT57cTQ1fTwvcHJlPjwvcD4KPHA+PHN0cm9uZz7lhbbku5booaXlhYXvvJo8L3N0cm9uZz48YnI+PHByZT57cTQ2fTwvcHJlPjwvcD4KCjxocj4KPHAgc3R5bGU9ImNvbG9yOiM3ZjhjOGQ7Zm9udC1zaXplOjAuOWVtOyI+5q2k6YKu5Lu255Sx5Y2D6Im655WM6Z2i6K+V562b6YCJ57O757uf6Ieq5Yqo55Sf5oiQ5bm25Y+R6YCB44CCPC9wPgo8L2JvZHk+CjwvaHRtbD4=").decode('utf-8').format(
        applicant_name=data.get('applicant_name','未填'),
        now=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
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
        q34=data.get('q34','未填'), q35=data.get('q35','未填'),
        q36_1=data.get('q36_1',''), q36_2=data.get('q36_2',''), q36_3=data.get('q36_3',''),
        q37=data.get('q37','未填'), q38=data.get('q38','未填'), q39=data.get('q39','未填'),
        q40=data.get('q40','未填'), q41=data.get('q41','未填'), q42=data.get('q42','未填'),
        q43=data.get('q43',''), q44=data.get('q44',''), q45=data.get('q45',''), q46=data.get('q46','')
    )
    return html

def generate_fresh_summary(data):
    _h = _IMPORT_('base64')
    html = _h.b64decode("PCFET0NUWVBFIGh0bWw+CjxodG1sPgo8aGVhZD4KPG1ldGEgY2hhcnNldD0idXRmLTgiPgo8c3R5bGU+CmJvZHkge3sgZm9udC1mYW1pbHk6ICdNaWNyb3NvZnQgWWFIZWknLCBzYW5zLXNlcmlmOyBsaW5lLWhlaWdodDoxLjY7IGNvbG9yOiMzMzM7IG1heC13aWR0aDo4MDBweDsgbWFyZ2luOjAgYXV0bzsgcGFkZGluZzoyMHB4OyB9fQpoMSB7eyBjb2xvcjojMmMzZTUwOyBib3JkZXItYm90dG9tOjJweCBzb2xpZCAjMDBhODg0OyBwYWRkaW5nLWJvdHRvbTo4cHg7IH19CmgyIHt7IGNvbG9yOiMwMDhjNmM7IG1hcmdpbi10b3A6MjRweDsgfX0KdGFibGUge3sgYm9yZGVyLWNvbGxhcHNlOmNvbGxhcHNlOyB3aWR0aDoxMDAlOyBtYXJnaW46MTJweCAwOyB9fQp0aCB7eyBiYWNrZ3JvdW5kOiNlY2YwZjE7IHRleHQtYWxpZ246bGVmdDsgcGFkZGluZzoxMHB4OyBib3JkZXI6MXB4IHNvbGlkICNiZGMzYzc7IH19CnRkIHt7IHBhZGRpbmc6MTBweDsgYm9yZGVyOjFweCBzb2xpZCAjYmRjM2M3OyB2ZXJ0aWNhbC1hbGlnbjp0b3A7IH19CnByZSB7eyBiYWNrZ3JvdW5kOiNmOGY5ZmE7IHBhZGRpbmc6MTJweDsgYm9yZGVyLWxlZnQ6NHB4IHNvbGlkICMwMGE4ODQ7IHdoaXRlLXNwYWNlOnByZS13cmFwOyB9fQoubWV0YSB7eyBjb2xvcjojN2Y4YzhkOyBmb250LXNpemU6MC45ZW07IG1hcmdpbi1ib3R0b206MjBweDsgfX0KPC9zdHlsZT4KPC9oZWFkPgo8Ym9keT4KPGgxPuWNg+iJuueVjCDCtyDlrqTlhoXorr7orqHluIjpnaLor5XnrZvpgInvvIjlupTlsYrnlJ/niYjvvIk8L2gxPgo8ZGl2IGNsYXNzPSJtZXRhIj7mj5DkuqTml7bpl7TvvJp7bm93fSB8IOmXruWNt+exu+Wei++8muW6lOWxiueUn+eJiCB8IOW6lOiBmOiAhe+8mnthcHBsaWNhbnRfbmFtZX08L2Rpdj4KCjxoMj7kuIDjgIHova/ku7bmioDog708L2gyPgo8dGFibGU+Cjx0cj48dGg+6L2v5Lu2PC90aD48dGg+5o6M5o+h56iL5bqmPC90aD48L3RyPgo8dHI+PHRkPkF1dG9DQUQgKENBRCk8L3RkPjx0ZD57cTF9PC90ZD48L3RyPgo8dHI+PHRkPlNrZXRjaFVwIChTVSk8L3RkPjx0ZD57cTJ9PC90ZD48L3RyPgo8dHI+PHRkPjNkcyBNYXggKDNEIE1heCk8L3RkPjx0ZD57cTN9PC90ZD48L3RyPgo8dHI+PHRkPkFkb2JlIFBob3Rvc2hvcCAoUFMpPC90ZD48dGQ+e3E0fTwvdGQ+PC90cj4KPHRyPjx0ZD5ENSBSZW5kZXIgKEQ1KTwvdGQ+PHRkPntxNX08L3RkPjwvdHI+Cjx0cj48dGQ+V1BTIE9mZmljZSAoV1BTKTwvdGQ+PHRkPntxNn08L3RkPjwvdHI+CjwvdGFibGU+Cgo8aDI+5LqM44CB5LiT5Lia5oqA6IO9PC9oMj4KPHRhYmxlPgo8dHI+PHRoPuaKgOiDvemhuTwvdGg+PHRoPuaOjOaPoeeoi+W6pjwvdGg+PC90cj4KPHRyPjx0ZD7ph4/miL/kuI7njrDlnLrli5jmtYs8L3RkPjx0ZD57cTd9PC90ZD48L3RyPgo8dHI+PHRkPuWutuijheiuvuiuoe+8iOS9j+WuheepuumXtO+8iTwvdGQ+PHRkPntxOH08L3RkPjwvdHI+Cjx0cj48dGQ+5bel6KOF6K6+6K6h77yI5ZWG5LiaL+WKnuWFrC/ppJDppa7nrYnvvIk8L3RkPjx0ZD57cTl9PC90ZD48L3RyPgo8dHI+PHRkPuaWveW3peWbvue7mOWItuS4jua3seWMljwvdGQ+PHRkPntxMTB9PC90ZD48L3RyPgo8dHI+PHRkPuaViOaenOWbvuihqOeOsO+8iOmdmeW4py/lhajmma8v5Yqo55S777yJPC90ZD48dGQ+e3ExMX08L3RkPjwvdHI+Cjx0cj48dGQ+6L2v6KOF5pCt6YWN5LiO5pGG5Zy6PC90ZD48dGQ+e3ExMn08L3RkPjwvdHI+CjwvdGFibGU+Cgo8aDI+5LiJ44CB5LiT5Lia6IOM5pmvPC9oMj4KPHA+PHN0cm9uZz7mnIDpq5jlrabljobvvJo8L3N0cm9uZz57cTEzfTwvcD4KPHA+PHN0cm9uZz7miYDlrabkuJPkuJrvvJo8L3N0cm9uZz57cTE0fTwvcD4KPHA+PHN0cm9uZz7lrp7kuaDnu4/ljobvvJo8L3N0cm9uZz57cTE1fTwvcD4KPHA+PHN0cm9uZz7lrp7kuaDmjqXop6bnjq/oioLvvJo8L3N0cm9uZz57cTE2fTwvcD4KCjxoMj7lm5vjgIHlr7nlrabmoKHkuI7lrp7kuaDnmoTmgJ3ogIM8L2gyPgo8cD48c3Ryb25nPuWtpuagoeefpeivhuacieeUqOaAp++8mjwvc3Ryb25nPntxMTd9PC9wPgo8cD48c3Ryb25nPuWtpuagoeacgOasoOe8uuaVmeeahOWGheWuue+8mjwvc3Ryb25nPntxMTh9PC9wPgo8cD48c3Ryb25nPuWunuS5oOacgOW4jOacm+iOt+W+l++8mjwvc3Ryb25nPntxMTl9PC9wPgo8cD48c3Ryb25nPuiHquWtpua4oOmBk++8mjwvc3Ryb25nPntxMjB9PC9wPgoKPGgyPuS6lOOAgeS4quS6uuWfuuacrOaDheWGtTwvaDI+CjxwPjxzdHJvbmc+5Ye655Sf5bm05Lu977yaPC9zdHJvbmc+e3EyMX08L3A+CjxwPjxzdHJvbmc+5piv5ZCm5pyJ55S3L+Wls+aci+WPi++8mjwvc3Ryb25nPntxMjJ9PC9wPgo8cD48c3Ryb25nPuWxheS9j+WfjuW4gi/ljLrln5/vvJo8L3N0cm9uZz57cTIzfTwvcD4KPHA+PHN0cm9uZz7pgJrli6Tml7bpl7TvvJo8L3N0cm9uZz57cTI0fTwvcD4KPHA+PHN0cm9uZz7mnJ/mnJvolqrotYTvvJo8L3N0cm9uZz57cTI1fSDlhYMv5pyIPC9wPgo8cD48c3Ryb25nPuacgOW/q+WIsOWyl+aXtumXtO+8mjwvc3Ryb25nPntxMjZ9PC9wPgoKPGgyPuWFreOAgeiBjOS4muaAgeW6puS4juS7t+WAvOingjwvaDI+CjxwPjxzdHJvbmc+56ys5LiA5Lu95bel5L2c6YCJ5oup5Zug57Sg5o6S5bqP77yaPC9zdHJvbmc+IDEue3EyN18xfSAyLntxMjdfMn0gMy57cTI3XzN9PC9wPgo8cD48c3Ryb25nPuWvueWKoOePreeahOaAgeW6pu+8mjwvc3Ryb25nPntxMjh9PC9wPgo8cD48c3Ryb25nPuacquadpTPlubTogYzkuJrop4TliJLvvJo8L3N0cm9uZz57cTI5fTwvcD4KCjxoMj7kuIPjgIHmg4Xmma/liKTmlq08L2gyPgo8cD48c3Ryb25nPuWPjeWkjeaUueWbvuW6lOWvue+8mjwvc3Ryb25nPntxMzB9PC9wPgo8cD48c3Ryb25nPuiiq+aWveW3peW4iOWCheaAvO+8mjwvc3Ryb25nPntxMzF9PC9wPgo8cD48c3Ryb25nPumZjOeUn+mjjuagvOW/q+mAn+WHuuaWueahiO+8mjwvc3Ryb25nPntxMzJ9PC9wPgoKPGgyPuWFq+OAgeW8gOaUvumimDwvaDI+CjxwPjxzdHJvbmc+5L2c5ZOB6ZuG6ZO+5o6l77yaPC9zdHJvbmc+PGJyPntxMzN9PC9wPgo8cD48c3Ryb25nPuavleS4muiuvuiuoeS7i+e7je+8mjwvc3Ryb25nPjxicj48cHJlPntxMzR9PC9wcmU+PC9wPgo8cD48c3Ryb25nPuaso+i1j+eahOiuvuiuoeW4iC/kvZzlk4HvvJo8L3N0cm9uZz48YnI+PHByZT57cTM1fTwvcHJlPjwvcD4KPHA+PHN0cm9uZz7lhbbku5booaXlhYXvvJo8L3N0cm9uZz48YnI+PHByZT57cTM2fTwvcHJlPjwvcD4KCjxocj4KPHAgc3R5bGU9ImNvbG9yOiM3ZjhjOGQ7Zm9udC1zaXplOjAuOWVtOyI+5q2k6YKu5Lu255Sx5Y2D6Im655WM6Z2i6K+V562b6YCJ57O757uf6Ieq5Yqo55Sf5oiQ5bm25Y+R6YCB44CCPC9wPgo8L2JvZHk+CjwvaHRtbD4=").decode('utf-8').format(
        applicant_name=data.get('applicant_name','未填'),
        now=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        q1=data.get('q1','未填'), q2=data.get('q2','未填'), q3=data.get('q3','未填'),
        q4=data.get('q4','未填'), q5=data.get('q5','未填'), q6=data.get('q6','未填'),
        q7=data.get('q7','未填'), q8=data.get('q8','未填'), q9=data.get('q9','未填'),
        q10=data.get('q10','未填'), q11=data.get('q11','未填'), q12=data.get('q12','未填'),
        q13=data.get('q13','未填'), q14=data.get('q14','未填'), q15=data.get('q15','未填'),
        q16=data.get('q16','未填'), q17=data.get('q17','未填'), q18=data.get('q18','未填'),
        q19=data.get('q19','未填'), q20=data.get('q20','未填'),
        q21=data.get('q21','未填'), q22=data.get('q22','未填'), q23=data.get('q23','未填'),
        q24=data.get('q24','未填'), q25=data.get('q25','未填'), q26=data.get('q26','未填'),
        q27_1=data.get('q27_1',''), q27_2=data.get('q27_2',''), q27_3=data.get('q27_3',''),
        q28=data.get('q28','未填'), q29=data.get('q29','未填'),
        q30=data.get('q30','未填'), q31=data.get('q31','未填'), q32=data.get('q32','未填'),
        q33=data.get('q33',''), q34=data.get('q34',''), q35=data.get('q35',''), q36=data.get('q36','')
    )
    return html

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8765))
    app.run(host="0.0.0.0", port=port, debug=False)