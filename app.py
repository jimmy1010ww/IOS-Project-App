
import logging
import random
from flask import Flask, render_template, request
from flask import jsonify
from bs4 import BeautifulSoup
from moodle_bot import MoodleBot

app = Flask(__name__)
# 這個應用程式會創建一個 Flask 實例，並將 /hello 網址綁定到 hello() 函數。
# 當使用 GET 請求訪問 /hello 時，如果指定了 name 參數，它將使用該參數來回應訊息。如果未指定 name 參數，則使用 "World" 作為預設值。
#當使用 POST 請求訪問 /hello 時，它將從請求表單中獲取 name 參數並回應訊息。

flask_logger = logging.getLogger('flask')
flask_logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('[Flask Logger]%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
console_handler = logging.StreamHandler()
console_handler.formatter = formatter
console_handler.setLevel(logging.DEBUG)
flask_logger.addHandler(console_handler)


moodleBot_list = []
userid_list = []

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
def check_moodle_login():
    #如果是POST請求，從請求獲取json來進行登入
    if request.method == 'POST':
        #印出請求方式
        flask_logger.debug("[Receive] POST request]")
        
        #印出Clien IP和Port
        flask_logger.info("Client IP : {}".format(str(request.remote_addr)))
        flask_logger.info("Clinet Port : {}".format(str(request.environ['REMOTE_PORT'])))

        # 取得新的 userid
        if userid_list == []:
            userid_list.append(0)
        else:   
            userid_list.append(userid_list[-1]+1)
        flask_logger.info("userid : {}".format(str(userid_list[-1])))

        #從請求獲取json
        data = request.get_json()

        #從json中獲取帳號密碼
        username = data['username']
        password = data['password']
        flask_logger.info("username : {} password: {}".format(str(username), str(password)))
        
        #宣告moodleLogin物件
        current_moodleBot = MoodleBot(username, password, userid_list[-1])
        
        #如果登入成功，回傳json
        if current_moodleBot.login():
            flask_logger.info("Login Success")
            flask_logger.info("userid : {}".format(str(userid_list[-1])))
            flask_logger.debug("moodleBot_list length : {}".format(str(len(moodleBot_list))))

            # 登入成功，新增 moodleBot 物件到 moodleBot_list
            moodleBot_list.append(current_moodleBot)
            return_data = jsonify({'result': 'success',
                            'userid': str(userid_list[-1])})
            flask_logger.debug("return_data : {}".format(return_data.json))
            return return_data
        else:
            userid_list.remove(userid_list[-1])
            flask_logger.warning("Login Failed")
            flask_logger.debug("moodleBot_list length : {}".format(str(len(moodleBot_list))))
            return jsonify({'result': 'fail'})
    #如果不是POST請求，回傳錯誤
    else:
        flask_logger.warning("[Receive] invalid request method")
        return jsonify({'result': 'invalid request method'})
    
if __name__ == '__main__':
    app.run(debug=True)

    