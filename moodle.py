import asyncio
import time
import random
import requests
from pyppeteer import launch
from bs4 import BeautifulSoup

class moodleLogin:
    # 登入網址
    login_url = 'https://moodle2.ntust.edu.tw/login/index.php'
    target_url = 'https://moodle2.ntust.edu.tw/my/'

    # 建構式
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = requests.Session()
        


    # 登入
    async def login(self):
        # 開啟瀏覽器，設定headless=False可以顯示瀏覽器視窗
        browser = await launch(headless=False)

        # 創建一個新的頁面 
        page = await browser.newPage()

        # 前往登入頁面
        await page.goto(moodleLogin.login_url)  

        # 輸入帳號密碼
        await page.type('#username', self.username)
        await page.type('#password', self.password)

        # 模擬點擊登入按鈕
        await page.click('#loginbtn')
        
        # 等待頁面載入完成
        await asyncio.sleep(1)
        
        # 檢查是否登入成功
        # 取的pypeeter的html
        html = await page.content()
        soup = BeautifulSoup(html, 'html.parser')
        div = soup.find('div', {'class': 'alert alert-danger', 'role': 'alert'})
        if div == "登入無效，請重試":
            print('登入失敗')
            return False

        # pypeeter的session給requests用
        cookies_list = await page.cookies()
        cookies_dict = {cookie["name"]: cookie["value"] for cookie in cookies_list}
        self.session.cookies.update(cookies_dict)

        # 關閉瀏覽器
        await browser.close()
        return True

        


def input_time_random():
    return random.randint(100, 151)


# mymoodle = moodleLogin('B10915003', "A9%t347169")
# asyncio.get_event_loop().run_until_complete(mymoodle.login())