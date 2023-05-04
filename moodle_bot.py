import os
import logging
import requests
# from seleniumwire import webdriver
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

class MoodleBot:
    login_url = 'https://moodle2.ntust.edu.tw/login/index.php'
    home_page_url = 'https://moodle2.ntust.edu.tw/my/'
    service_url = "https://moodle2.ntust.edu.tw/lib/ajax/service.php?"
    def __init__(self, username, password, bot_id):
        # init variables
        self.username = username
        self.password = password
        self.bot_id = bot_id
        self.driver = None
        self.sskey = None
        
        # Init logger 
        
        # create logger
        self.logger = logging.getLogger('moodle.{}'.format(str(self.bot_id)))
        # set logger level
        self.logger.setLevel(logging.DEBUG)
        # create formatter
        formatter = logging.Formatter('[Moodle Bot Logger]%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        
        # create console handler and set level to debug
        console_handler = logging.StreamHandler()
        # add formatter to console_handler
        console_handler.formatter = formatter
        # set console_handler level
        console_handler.setLevel(logging.DEBUG)

        # add console handler to logger
        self.logger.addHandler(console_handler)

        self.logger.debug("Moodle Bot {} init...".format(str(self.bot_id)))
        self.logger.debug("username : {} password: {}".format(str(self.username), str(self.password)))
        self.initDriver()
        self.logger.info("Moodle Bot {} init done".format(str(self.bot_id)))

    def initDriver(self):
        # check if driver is already created
        try:
            if self.driver != None:
                self.driver = None 
        # catch the driver not created exception
        except Exception as e:
            self.logger.warning(str(e))
            self.logger.warning("driver not created")

        # configure chrome driver options
        chrome_options = Options() 
        # chrome_options.add_argument('--headless')  # 啟動Headless 無頭
        chrome_options.add_argument('--disable-gpu') #關閉GPU 避免某些系統或是網頁出錯
        chrome_options.add_argument('--log-level=2') #INFO = 0 WARNING = 1 LOG_ERROR = 2 LOG_FATAL = 3 default = 0
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])

        # configure chrome driver service
        service = Service(executable_path=os.path.abspath("\driver\chromedriver"))

        # create chrome driver
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.logger.debug("driver created")

    def login(self):
        self.logger.debug("login")

        
        self.driver.get(self.login_url)

        # Find the email and password fields
        email_field = self.driver.find_element(By.ID, "username")
        password_field = self.driver.find_element(By.ID, "password")
        login_button = self.driver.find_element(By.ID, "loginbtn")

        # Enter login credentials
        email_field.send_keys(self.username)
        password_field.send_keys(self.password)

        login_button.click()

        try:
            self.driver.implicitly_wait(5)

            # look if there is a login error element
            if self.driver.current_url == self.login_url:
                self.logger.warning("login url is the same")
                login_error_element = self.driver.find_element(By.XPATH, "//*[@id=\"region-main\"]/div/div[3]/div/div[1]/div")
                self.logger.warning(login_error_element.text)
                return False
            elif self.driver.current_url == self.home_page_url:
                self.logger.info("Login Success")
                self.sskey = self.driver.find_element(By.XPATH, "//*[@id=\"page-header\"]/div/div/div/div[2]/div[1]/div/form/input[2]")
                self.logger.info("sskey: {}".format(self.sskey.get_attribute("value")))
                return True

        except TimeoutError as e:
            self.logger.warning(str(e))
            self.logger.warning("Timeout")
            try:
                if self.driver.current_url == self.login_url:
                    self.logger.warning("login url is the same")
                    login_error_element = self.driver.find_element(By.XPATH, "//*[@id=\"region-main\"]/div/div[3]/div/div[1]/div")
                    self.logger.warning(login_error_element.text)
                    return False
            except Exception as e:
                self.logger.warning(str(e))
                self.logger.critical("Unexpeted error")
                return False
        except Exception as e:
            self.logger.warning(str(e))
            self.logger.critical("Unexpeted error")
            return False
    
    def close(self):
        self.driver.quit()

    def get_enrolled_courses_by_timeline_classification(self):
        session = requests.Session()
        
        # 把 cookie 設定到 session
        for cookie in self.driver.get_cookies():
            name = cookie['name']
            value = cookie['value']
            session.cookies.set(name, value)

        # 設定 request header
        session.headers.update({
            'User-Agent': self.driver.execute_script("return navigator.userAgent;"),
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Accept': '*/*',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://moodle2.ntust.edu.tw',
            'Referer': 'https://moodle2.ntust.edu.tw/my/',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7'
        })

def test():
    bot = MoodleBot("b10915003", "A9%t376149", 1)
    bot.login()
    bot.get_enrolled_courses_by_timeline_classification()
    input("Press Enter to continue...")
test()