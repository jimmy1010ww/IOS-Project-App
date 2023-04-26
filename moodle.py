import asyncio
import time
import random
# import requests
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
        self.page = None

    # 登入
    async def getLoginPage(self):
        browser = await launch(headless=False)  # 開啟瀏覽器，設定headless=False可以顯示瀏覽器視窗
        page = await browser.newPage()  # 創建一個新的頁面
        await page.goto(moodleLogin.login_url)  # 前往登入頁面
        return page
    
    async def getLogonCookie(self, page):
        # 輸入用戶名和密碼, {'delay': input_time_random() - 50}
        await page.type('#username', username)
        await page.type('#password',  password)

        await page.click('#loginbtn')
        await asyncio.sleep(3)
        
        # 取的登入後的 cookies
        cookies_list = await page.cookies()
        
        content = await page.content()
        return cookies_list, content



def input_time_random():
    return random.randint(100, 151)

username = "B10915003"
password = "A9%t376149"
mylogin = moodleLogin(username, password)

page = asyncio.get_event_loop().run_until_complete(mylogin.getLoginPage())
cookies, content = asyncio.get_event_loop().run_until_complete(mylogin.getLogonCookie(page))
#暫停
print(cookies)
#print(content)
input("Press Enter to continue...")