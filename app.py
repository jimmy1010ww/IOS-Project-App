import logging
import asyncio
import random
from flask import Flask, render_template, request
from flask import jsonify
from pyppeteer import launch
from bs4 import BeautifulSoup

app = Flask(__name__)
# 這個應用程式會創建一個 Flask 實例，並將 /hello 網址綁定到 hello() 函數。
# 當使用 GET 請求訪問 /hello 時，如果指定了 name 參數，它將使用該參數來回應訊息。如果未指定 name 參數，則使用 "World" 作為預設值。
#當使用 POST 請求訪問 /hello 時，它將從請求表單中獲取 name 參數並回應訊息。

# 暫存所有登入的狀態
login_status = {}

login_url = 'https://moodle2.ntust.edu.tw/login/index.php'
target_url = 'https://moodle2.ntust.edu.tw/my/'

logging.basicConfig(
    level=logging.DEBUG, 
    format='%(asctime)s %(levelname)-8s %(message)s', 
    datefmt='%Y-%m-%d %H:%M:%S'
)

async def login(username, password):
        # 開啟瀏覽器，設定headless=False可以顯示瀏覽器視窗
        browser = await launch( headless=True,
                                handleSIGINT=False,
                                handleSIGTERM=False,
                                handleSIGHUP=False)

        # 創建一個新的頁面 
        page = await browser.newPage()

        # 前往登入頁面
        await page.goto(login_url)  

        # 輸入帳號密碼
        await page.type('#username', username)
        await page.type('#password', password)

        # 模擬點擊登入按鈕
        await page.click('#loginbtn')
        
        # 等待頁面載入完成
        await asyncio.sleep(1)

        if page.url == login_url:
            html = await page.content()
            logging.debug(html)
            soup = BeautifulSoup(html, 'html.parser')
            div = soup.find('div', {'class': 'alert alert-danger', 'role': 'alert'})
            print("div: {}".format(div))
            if "登入無效，請重試" in div:
                print('登入失敗')
                return False
        
        # pypeeter的session給requests用
        # cookies_list = await page.cookies()
        # cookies_dict = {cookie["name"]: cookie["value"] for cookie in cookies_list}
        # self.session.cookies.update(cookies_dict)

        # 關閉瀏覽器
        # await browser.close()
        return True

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

        logging.debug("[Receive] POST request]")

        #從請求獲取json
        data = request.get_json()
        #從json中獲取帳號密碼
        username = data['username']
        password = data['password']
        logging.info("username : {} password: {}".format(str(username), str(password)))
        
        #宣告moodleLogin物件
        result = asyncio.run(login(username, password))

        #如果登入成功，回傳json
        if result:
            logging.info("Login Sucess")
            return jsonify({'result': 'success'})
        else:
            logging.warning("Login Failed")
            return jsonify({'result': 'fail'})
    #如果不是POST請求，回傳錯誤
    else:
        return jsonify({'result': 'invalid request method'})
    
if __name__ == '__main__':
    app.run(debug=True)
    