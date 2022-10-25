from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def home():
   return render_template("monthlyDiary.html",title="정글 다이어리")

if __name__ == '__main__':  
   app.run('0.0.0.0',port=5000,debug=True)