from flask import Flask, render_template, request
from flask import jsonify
from moodle import moodleLogin, asyncio

app = Flask(__name__)
loop = asyncio.new_event_loop()
# 這個應用程式會創建一個 Flask 實例，並將 /hello 網址綁定到 hello() 函數。
# 當使用 GET 請求訪問 /hello 時，如果指定了 name 參數，它將使用該參數來回應訊息。如果未指定 name 參數，則使用 "World" 作為預設值。
#當使用 POST 請求訪問 /hello 時，它將從請求表單中獲取 name 參數並回應訊息。

@app.route('/hello', methods=['GET', 'POST'])
def hello():
    if request.method == 'POST':
        name = request.form['name']
        return f'Hello, {name}!'
    else:
        name = request.args.get('name', 'World')
        return f'Hello, {name}!'

# API

# 檢查moodle是否可以正確登入
@app.route('/api/check_moodle_login', methods=['POST'])
@pypeeter.asyncio
async def api():
    #如果是POST請求，從請求獲取json來進行登入
    if request.method == 'POST':
        #從請求獲取json
        data = request.get_json()
        #從json中獲取帳號密碼
        username = data['username']
        password = data['password']
        print(username, password)
        
        #宣告moodleLogin物件
        mymoodle = moodleLogin(username, password)
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(mymoodle.login())
        #如果登入成功，回傳json
        if result:
            return jsonify({'result': 'success'})
        else:
            return jsonify({'result': 'fail'})
    #如果不是POST請求，回傳錯誤
    else:
        return jsonify({'result': 'invalid request method'})
    
if __name__ == '__main__':
    app.run(debug=True)