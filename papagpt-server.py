import requests
import openai
import os
from dotenv import load_dotenv
from flask import Flask, request, render_template, redirect, url_for, make_response
from DB import DB

db = DB('papagpt','유저명','비밀번호')

load_dotenv()

GPT_API_KEY = os.getenv("GPT_API")
NAVER_CLIENT_SECRET = os.getenv("X-Naver-Client-Secret")
NAVER_CLIENT_ID = os.getenv("X-Naver-Client-Id")

app = Flask(__name__)

def translate_text(source, target, text):
    url = "https://openapi.naver.com/v1/papago/n2mt"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Naver-Client-Id":  NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    data = {
        "source": source,
        "target": target,
        "text": text
    }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        result = response.json()
        translated_text = result['message']['result']['translatedText']
        return translated_text
    else:
        return f"오류: {response.status_code}, {response.text}"
    
def chatGPT(text):
    
    openai.api_key = GPT_API_KEY 

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
         {"role": "user", "content": text},
        ],
        temperature=0,
        max_tokens=2048
    )
    content = completion['choices'][0]['message']['content']
    return content

def papagpt(input_text):
    ID = request.cookies.get('ID')
    translated_text = translate_text("ko", "en", input_text)
    GPT_ANS = chatGPT(translated_text)
    output = translate_text("en", "ko", GPT_ANS)
    db.chat(ID,input_text, output)
    return output

@app.route('/', methods=['POST','GET'])
def main():
    ID = request.cookies.get('ID')
    if ID:
        if request.method == 'POST':
            input_text = request.form.get("user_input")
            papagpt(input_text)
            chatlog = db.select_log(ID)
            return redirect(url_for("main"))
        else:
            chatlog = db.select_log(ID)
            return render_template("main.html",chatlog=chatlog, ID=ID)
    else:    
        return render_template("main.html")


@app.route("/join", methods=['POST', 'GET'])
def join():
    if request.method == 'POST':
        userID = request.form.get("userID")
        PW1 = request.form.get("PW1")
        PW2 = request.form.get("PW2")

        if db.select_user(userID):
            return render_template('join.html', message='이미 존재하는 아이디입니다.')
        elif PW1 == PW2:
            db.insert_user(userID, PW1)
            return render_template('join.html', message='회원가입되었습니다.', clear=True)
        else:
            return render_template('join.html', message='비밀번호가 일치하지 않습니다. 다시 입력해주세요.')
    return render_template('join.html')

@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        userID = request.form.get("userID")
        password = request.form.get("password")
        
        if db.select_user_password(userID, password):
            resp = make_response(redirect(url_for('main')))
            resp.set_cookie('ID', userID)
            return resp
        else:
            return render_template('login.html', message='아이디 또는 비밀번호가 일치하지 않습니다.')
    return render_template("login.html")

@app.route("/logout")
def logout():
    resp = make_response(redirect(url_for('main')))
    resp.delete_cookie('ID')
    return resp

@app.route("/quit")
def quit():
    ID = request.cookies.get('ID')
    if ID:
        db.delete_user(ID)
        resp = make_response(redirect(url_for('logout')))
        return resp
    else:
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)