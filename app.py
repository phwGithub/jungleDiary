from flask import Flask, request, render_template, jsonify, make_response, redirect, url_for
from pymongo import MongoClient 
# 왜인지 hashlib 설치가 되지 않음 
import hashlib
import jwt
from datetime import datetime, timedelta

app = Flask(__name__)

SECRET_KEY = 'KRAFTONJUNGLE' 

client = MongoClient('localhost', 27017)  # 로컬연결
db = client.db_jungle_local


# @app.route('/')
# def home():
#     token_receive = request.cookies.get('mytoken')
#     try:
#         payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

#         return render_template('index.html')
#     except jwt.ExpiredSignatureError:
#         return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
#     except jwt.exceptions.DecodeError:
#         return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

# @app.route('/login')
# def login():
#     msg = request.args.get("msg")
#     return render_template('login.html', msg=msg)


@app.route('/signup', methods=['POST'])
def sign_up():
    new_name = request.form['new_name_give']
    new_pwd = request.form['new_pwd_give']
    result = db.jgDiary.insert_one({'name': new_name, 'password': new_pwd})


# @app.route('/signin', methods=['POST'])
# def sign_in():
#     username_receive = request.form['username_give']
#     password_receive = request.form['password_give']


#     pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
#     result = db.users.find_one({'username': username_receive, 'password': pw_hash})

#     if result is not None:  #result 찾음
#         payload = {
#             'id': username_receive,
#             'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
#         }
#         token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')

#         return jsonify({'result': 'success', 'token': token})
#     # result 못찾음
#     else:
#         return jsonify({'result': 'fail', 'msg': '가입하지 않은 아이디이거나, 잘못된 비밀번호입니다.'})


if __name__ == '__main__':  
   app.run('0.0.0.0',port=5000,debug=True)