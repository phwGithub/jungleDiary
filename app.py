import time
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.json_util import dumps
from flask import Flask, request, render_template, jsonify
import hashlib
import jwt
from datetime import datetime, timedelta

app = Flask(__name__)
client = MongoClient('localhost', 27017)  # 로컬연결
db = client.jgDiary

SECRET_KEY = 'KRAFTONJUNGLE'

def validate_token(token):
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms='HS256')
    except jwt.ExpiredSignatureError:
        return '토큰만료'
    except jwt.InvalidTokenError:
        return '유효하지않은토큰'
    else:
        return decoded

    ### api로 서버로 요청받았을때 토큰 검증 양식
    # token = request.cookies.get('mytoken')
    # if validate_token(token) == '토큰만료':
    #     return jsonify({'result': 'fail','msg':'토큰이 만료되었습니다!'})
    # elif validate_token(token) =='유효하지않은토큰':
    #     return jsonify({'result': 'fail','msg':'토큰이 유효하지 않습니다'})
    # else:

# 메인 페이지 토큰 검증 후 페이지 렌더링
@app.route('/')
def home():
    token = request.cookies.get('mytoken')
    if (validate_token(token) == '토큰만료') or (validate_token(token) == '유효하지않은토큰'):
        return render_template("sign_in.html", title="정글 다이어리")
    else:
        date = time.strftime('%Y %m %d %a', time.localtime(time.time()))
        now_date = date.split(' ')
        return render_template('main.html', title="오늘의 메모", date=now_date)


# 회원가입 페이지로 이동
@app.route('/sign_up', methods=['GET'])
def render_sign_up():
    return render_template('sign_up.html')

# 로그인 페이지로 이동
@app.route('/sign_in', methods=['GET'])
def render_sign_in():
    return render_template('sign_in.html')

# 가입하기
@app.route('/sign_up', methods=['POST'])
def sign_up():
    new_name = request.form['new_name_give']
    new_pwd = request.form['new_pwd_give']
    result = db.user.find_one({'name': new_name})
    print("여기")
    # db에 이름이 이미 있는지 확인하기
    if result is None:
        password_hash = hashlib.sha256(new_pwd.encode('utf-8')).hexdigest()
        doc = {
            "name": new_name,
            "pwd": password_hash,
        }
        db.user.insert_one(doc)
        return jsonify({'result': 'success', 'msg': 'DB에 유저 등록 완료'})
    else:
        return jsonify({'result': 'fail', 'msg': '동일한 이름을 가진 유저가 있어서 DB에 등록 실패'})

# 로그인하기
@app.route('/sign_in', methods=['POST'])
def sign_in():
    username_receive = request.form['input_name']
    password_receive = request.form['input_pwd']

    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.user.find_one({'name': username_receive, 'pwd': password_hash})

    # 아이디와 유저가 입력한 해쉬화된 pw가 DB에 저장되어 있는 해쉬화된 pw와 일치하는지 확인
    if result is not None:  # result 찾음
        payload = {
            'id': username_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        return jsonify({'result': 'success', 'msg': '로그인 성공', 'token': token})
    else:   # result 못찾음
        return jsonify({'result': 'fail', 'msg': '가입하지 않은 아이디이거나, 잘못된 비밀번호입니다.'})

# 메인 화면 보여주기
@app.route('/mainpage')
def mainpage():
    token = request.cookies.get('mytoken')
    if validate_token(token) == '토큰만료':
        return render_template('sign_in.html', msg="로그인이 필요합니다.")
    elif validate_token(token) =='유효하지않은토큰':
        return render_template('sign_in.html', msg="로그인이 필요합니다.")
    else:
        date = time.strftime('%Y %m %d %a', time.localtime(time.time()))
        now_date = date.split(' ')
    return render_template('main.html', title="오늘의 메모", date=now_date)

# 나의 일기 보여주기
@app.route('/showMyDiary')
def showMyDiary():
    token = request.cookies.get('mytoken')
    if validate_token(token) == '토큰만료':
        return render_template('sign_in.html', msg="로그인이 필요합니다.")
    elif validate_token(token) =='유효하지않은토큰':
        return render_template('sign_in.html', msg="로그인이 필요합니다.")
    else:
        token = validate_token(token)
        date = time.strftime('%Y %m %d %a', time.localtime(time.time()))
        now_date = date.split(' ')
    return render_template('monthlyDiary.html', title="나의 일기", date=now_date, mytoken=token)

# 모두의 일기 보여주기
@app.route('/showEveryDiary')
def showEveryDiary():
    token = request.cookies.get('mytoken')
    if validate_token(token) == '토큰만료':
        return render_template('sign_in.html', msg="로그인이 필요합니다.")
    elif validate_token(token) =='유효하지않은토큰':
        return render_template('sign_in.html', msg="로그인이 필요합니다.")
    else:
        token = validate_token(token)
        date = time.strftime('%Y %m %d %a', time.localtime(time.time()))
        now_date = date.split(' ')
    return render_template('monthlyDiary.html', title="모두의 일기", date=now_date, mytoken=token)

# 메모 작성 (완)
@app.route('/api/appendMemo', methods=['post'])
def appendMemos():
    token = request.cookies.get('mytoken')
    if validate_token(token) == '토큰만료':
        return jsonify({'result': 'fail','msg':'토큰이 만료되었습니다!'})
    elif validate_token(token) =='유효하지않은토큰':
        return jsonify({'result': 'fail','msg':'토큰이 유효하지 않습니다'})
    else:
        appending_user = validate_token(token)['id']
        new_memo = request.form['new_memo']
        new_memo_date = int(time.strftime('%Y%m%d', time.localtime(time.time())))
        new_memo_time = int(time.strftime('%H%M%S', time.localtime(time.time())))
        db.memos.insert_one({'user': appending_user, 'content': new_memo,'date': new_memo_date, 'time': new_memo_time})
        return jsonify({'result': 'success'})

# 메모 불러오기(완)
@app.route('/api/getMemos', methods=['get'])
def getMemos():
    token = request.cookies.get('mytoken')
    if validate_token(token) == '토큰만료':
        return jsonify({'result': 'fail','msg':'토큰이 만료되었습니다!'})
    elif validate_token(token) =='유효하지않은토큰':
        return jsonify({'result': 'fail','msg':'토큰이 유효하지 않습니다'})
    else:
        memo_date = int(time.strftime('%Y%m%d', time.localtime(time.time())))
        memo_user = validate_token(token)['id']
        memos = db.memos.find({'user': memo_user, 'date': memo_date}).sort('time', -1)
        user_memos = dumps(memos)
        return jsonify({'result': 'success', 'user_memos': user_memos})


# 메모 삭제(완)
@app.route('/api/deleteMemo', methods=['post'])
def deleteMemo():
    token = request.cookies.get('mytoken')
    if validate_token(token) == '토큰만료':
        return jsonify({'result': 'fail','msg':'토큰이 만료되었습니다!'})
    elif validate_token(token) =='유효하지않은토큰':
        return jsonify({'result': 'fail','msg':'토큰이 유효하지 않습니다'})
    else:
        delete_memo_id = request.form['delete_memo_id']
        db.memos.delete_one({'_id': ObjectId(delete_memo_id)})
        return jsonify({'result': 'success'})

# 메모 수정(완)
@app.route('/api/updateMemo', methods=['post'])
def updateMemo():
    token = request.cookies.get('mytoken')
    if validate_token(token) == '토큰만료':
        return jsonify({'result': 'fail','msg':'토큰이 만료되었습니다!'})
    elif validate_token(token) =='유효하지않은토큰':
        return jsonify({'result': 'fail','msg':'토큰이 유효하지 않습니다'})
    else:
        update_memo_id = request.form['update_memo_id']
        update_memo = request.form['update_memo']
        db.memos.update_one({'_id': ObjectId(update_memo_id)},{'$set': {'content': update_memo}})
        return jsonify({'result': 'success'})

# 일기 작성(완) 아래 주석에 사용법
@app.route('/api/appendDiary', methods=['post'])
def appendDiary():
    token = request.cookies.get('mytoken')
    if validate_token(token) == '토큰만료':
        return jsonify({'result': 'fail','msg':'토큰이 만료되었습니다!'})
    elif validate_token(token) =='유효하지않은토큰':
        return jsonify({'result': 'fail','msg':'토큰이 유효하지 않습니다'})
    else:
        new_diary_user = validate_token(token)['id']
        new_diary_title = request.form['new_diary_title']
        new_diary_content = request.form['new_diary_content']
        new_diary_date = request.form['new_diary_date']
        new_diary_time = int(time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())))
        db.diary.insert_one({'user': new_diary_user, 'title': new_diary_title,'content': new_diary_content, 'fixed_date': new_diary_date, 'update_time': new_diary_time, 'likes' : 0})
        return jsonify({'result': 'success'})


# 일기 불러오기 아래 주석에 사용 법
# function appendDiary(date) {
#     memo_wrtie_form();
#     let new_diary_title = $('#diary_title').val();
#     let new_diary_content = $('#diary_content').val();
#     $.ajax({
#         type: "POST",
#         url: "/api/appendDiary",
#         data: {'new_diary_title':new_diary_title,'new_diary_content': new_diary_content,'new_diary_date':date},
#         success: function (response) {
#             if (response["result"] === "success") {
#                 getMemos();
#             }
#             else if(response.result =='fail'){
#                 alert(response['msg']);
#                 window.location.replace("/sign_in");
#             }
#             else {
#                 alert("서버 오류!");
#             }
#         }
#     })

# }

# 내 일기 불러오기
@app.route('/api/getDiary', methods=['get'])
def getDiary():
    ## api로 서버로 요청받았을때 토큰 검증 양식
    token = request.cookies.get('mytoken')
    if validate_token(token) == '토큰만료':
        return jsonify({'result': 'fail','msg':'토큰이 만료되었습니다!'})
    elif validate_token(token) =='유효하지않은토큰':
        return jsonify({'result': 'fail','msg':'토큰이 유효하지 않습니다'})
    else:
        get_diary_user = validate_token(token)['id']
        get_diary_date = request.args.get('get_diary_date')
        diary = db.diary.find({'user': get_diary_user, 'fixed_date': get_diary_date}).sort('fixed_time', 1)
        get_diary_list = dumps(diary)
    return jsonify({'result': 'success', 'get_diary_list': get_diary_list})

# 날짜별 모두의 일기 불러오기
@app.route('/api/getEveryDiary', methods=['get'])
def getEveryDiary():
    ## api로 서버로 요청받았을때 토큰 검증 양식
    token = request.cookies.get('mytoken')
    if validate_token(token) == '토큰만료':
        return jsonify({'result': 'fail','msg':'토큰이 만료되었습니다!'})
    elif validate_token(token) =='유효하지않은토큰':
        return jsonify({'result': 'fail','msg':'토큰이 유효하지 않습니다'})
    else:
        get_diary_date = request.args.get('get_diary_date')
        diary = db.diary.find({'fixed_date': get_diary_date}).sort('likes', -1)
        get_diary_list = dumps(diary)
    return jsonify({'result': 'success', 'get_diary_list': get_diary_list})

# 일기 수정
@app.route('/api/updateDiary', methods=['post'])
def updateDiary():
    ## api로 서버로 요청받았을때 토큰 검증 양식
    token = request.cookies.get('mytoken')
    if validate_token(token) == '토큰만료':
        return jsonify({'result': 'fail','msg':'토큰이 만료되었습니다!'})
    elif validate_token(token) =='유효하지않은토큰':
        return jsonify({'result': 'fail','msg':'토큰이 유효하지 않습니다'})
    else:
        update_diary_id = request.form['update_diary_id']
        update_diary_title = request.form['update_diary_title']
        update_diary_content = request.form['update_diary_content']
        update_diary_time = int(time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())))
        db.diary.update_one({'_id':ObjectId(update_diary_id)},{'$set':{'title':update_diary_title,'content':update_diary_content,'update_date':update_diary_time}})
    return jsonify({'result': 'success'})

# 일기 삭제
@app.route('/api/deleteDiary', methods=['post'])
def deleteDiary():
    token = request.cookies.get('mytoken')
    if validate_token(token) == '토큰만료':
        return jsonify({'result': 'fail','msg':'토큰이 만료되었습니다!'})
    elif validate_token(token) =='유효하지않은토큰':
        return jsonify({'result': 'fail','msg':'토큰이 유효하지 않습니다'})
    else:
        delete_diary_id = request.form['delete_diary_id']
        db.diary.delete_one({'_id': ObjectId(delete_diary_id)})
        return jsonify({'result': 'success'})

# 일기 좋아요
@app.route('/api/likeDiary', methods=['post'])
def likeDiary():
    token = request.cookies.get('mytoken')
    if validate_token(token) == '토큰만료':
        return jsonify({'result': 'fail','msg':'토큰이 만료되었습니다!'})
    elif validate_token(token) =='유효하지않은토큰':
        return jsonify({'result': 'fail','msg':'토큰이 유효하지 않습니다'})
    else:
        like_diary_id = request.form['like_diary_id']
        db.diary.update_one({'_id':ObjectId(like_diary_id)},{'$inc':{'likes': 1}})
        return jsonify({'result': 'success'})

# nav바 로그인 상태 체크하기
@app.route('/login_check', methods=['GET'])
def loginCheck():
    token = request.cookies.get('mytoken')
    if (validate_token(token) == '토큰만료') or (validate_token(token) == '유효하지않은토큰'):
        return jsonify({'result': 'fail', 'msg': '토큰이 만료되었거나 유효하지 않습니다'})
    else:
        name = validate_token(token)['id']
        return jsonify({'result': 'success', 'msg': '로그인 상태입니다', 'id':name })


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
