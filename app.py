import time
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.json_util import dumps
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

client = MongoClient('localhost',27017)
db = client.jgDiary

@app.route('/')
def home():
   return render_template("index.html",title="정글 다이어리")


### HTML 화면 보여주기
@app.route('/mainpage')
def mainpage():
    return render_template('main.html',title="오늘의 메모")

### 메모 작성
@app.route('/api/appendMemo', methods=['post'])
def appendMemos():
    appending_user = request.form['appending_user']
    new_memo = request.form['new_memo']
    new_memo_date = request.form['new_memo_date']
    new_memo_time = int(time.strftime('%H%M%S', time.localtime(time.time())))
    db.memos.insert_one({'user':appending_user,'content':new_memo,'date':new_memo_date, 'time': new_memo_time})
    return jsonify({'result': 'success'})

### 메모 불러오기
@app.route('/api/getMemos', methods=['get'])
def getMemos():
    memo_user = request.form['memo_user']
    memo_date = request.form['memo_date']
    memos = db.memos.find({'user': memo_user, 'date':memo_date}).sort('time',1)
    user_memos = dumps(memos)
    return jsonify({'result': 'success','user_memos':user_memos})


### 메모 삭제
@app.route('/api/deleteMemo', methods=['post'])
def deleteMemo():
    delete_memo_id = request.form['delete_memo_id']
    db.memos.delete_one({'_id':ObjectId(delete_memo_id)})
    return jsonify({'result': 'success'})

### 메모 수정
@app.route('/api/updateMemo', methods=['post'])
def updateMemo():
    update_memo_id = request.form['update_memo_id']
    update_memo = request.form['update_memo']
    db.memos.update_one({'_id':ObjectId(update_memo_id)},{'$set':{'content':update_memo}})
    return jsonify({'result': 'success'})

### 일기 작성
@app.route('/api/appendDiary', methods=['post'])
def appendDiary():
    new_diary_user = request.form['new_diary_user']
    new_diary_title = request.form['new_diary_title']
    new_diary_content = request.form['new_diary_content']
    new_diary_date = request.form['new_diary_date']
    new_diary_time = int(time.strftime('%y%m%d%H%M%S', time.localtime(time.time())))
    db.diary.insert_one({'user':new_diary_user,'title':new_diary_title,'content':new_diary_content,'fixed_date':new_diary_date, 'update_time':new_diary_time})
    return jsonify({'result': 'success'})
## 일기 불러오기
@app.route('/api/getDiary', methods=['get'])
def getDiary():
    get_diary_user = request.form['get_diary_user']
    get_diary_date = request.form['get_diary_date']
    diary = db.diary.find({'user': get_diary_user, 'date':get_diary_date}).sort('fixed_time',1)
    get_diary_list = dumps(diary)
    return jsonify({'result': 'success','get_diary_list':get_diary_list})


### 일기 수정
@app.route('/api/updateDiary', methods=['post'])
def updateDiary():
    update_diary_id = request.form['update_diary_id']
    update_diary_title = request.form['update_diary_title']
    update_diary_content = request.form['update_diary_content']
    update_diary_time = int(time.strftime('%y%m%d%H%M%S', time.localtime(time.time())))
    db.diary.update_one({'_id':ObjectId(update_diary_id)},{'$set':{'title':update_diary_title,'content':update_diary_content,'update_time':update_diary_time}})
    return jsonify({'result': 'success'})


if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)