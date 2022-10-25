from flask import Flask, request, render_template, jsonify, redirect, url_for
from pymongo import MongoClient 
import hashlib 
import jwt
from datetime import datetime, timedelta

app = Flask(__name__)
client = MongoClient('localhost', 27017)  # 로컬연결
db = client.db_jungle_local

SECRET_KEY = 'KRAFTONJUNGLE' 

@app.route('/')
def home():
    return render_template('sign_in.html')


@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('로그인성공.html', msg=msg)


@app.route('/sign_up', methods=['POST'])
def sign_up():
    new_name = request.form['new_name_give']
    new_pwd = request.form['new_pwd_give']
    password_hash = hashlib.sha256(new_pwd.encode('utf-8')).hexdigest()
    doc = {
        "name": new_name,
        "password": password_hash,
    }
    
    # todo/ db에 이미 있는지 확인하기 
    # same_user = db.jgDiary.find({'name':new_name}, {'_id':0})
    # if same_user:
    #     return jsonify({'result': 'fail', 'msg':'동일한 이름을 가진 유저가 있어서 DB에 등록 실패'})
    # else:
    db.jgDiary.insert_one(doc)
    return jsonify({'result': 'success', 'msg':'DB에 유저 등록 완료'})



@app.route('/sign_in', methods=['POST'])
def sign_in():
    username_receive = request.form['input_name']
    password_receive = request.form['input_pwd']

    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.jgDiary.find_one({'name': username_receive, 'password':password_hash})
    # 아이디와 유저가 입력한 해쉬화된 pw가 DB에 저장되어 있는 해쉬화된 pw와 일치하는지 확인 

    if result is not None:  #result 찾음
        payload = {
            'id': username_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'msg': '로그인 성공', 'token': token})
    
    else:   # result 못찾음
        return jsonify({'result': 'fail', 'msg': '가입하지 않은 아이디이거나, 잘못된 비밀번호입니다.'})


if __name__ == '__main__':  
   app.run('0.0.0.0',port=5000,debug=True)