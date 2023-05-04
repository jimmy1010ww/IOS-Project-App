import os
import logging
import colorlog
import requests
import json
import time
# from seleniumwire import webdriver
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

class MoodleBot:
    login_url = 'https://moodle2.ntust.edu.tw/login/index.php'
    home_page_url = 'https://moodle2.ntust.edu.tw/my/'
    service_url = "https://moodle2.ntust.edu.tw/lib/ajax/service.php?"
    def __init__(self, username, password, bot_id, headless=True):
        # init variables
        self.username = username
        self.password = password
        self.bot_id = bot_id
        self.driver = None
        self.sskey = None
        self.option_headless = headless
        
        # Init logger 
        
        # create logger
        self.logger = logging.getLogger('moodle_{}'.format(str(self.bot_id)))
        # set logger level
        self.logger.setLevel(logging.DEBUG)
        # create formatter
        formatter = colorlog.ColoredFormatter(
            '[Moodle Bot Logger] %(asctime)s %(log_color)s%(levelname)-8s%(reset)s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )
        
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
        if self.option_headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu') #關閉GPU 避免某些系統或是網頁出錯
        chrome_options.add_argument('--log-level=2') #INFO = 0 WARNING = 1 LOG_ERROR = 2 LOG_FATAL = 3 default = 0
        # chrome_options.add_argument('--proxy-server="direct://"')
        # chrome_options.add_argument('--proxy-bypass-list=*')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])

        # configure chrome driver service
        service = Service(executable_path=os.path.abspath("\driver_win\chromedriver"))

        # create chrome driver
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.logger.debug("driver created")

    def __del__(self):
        # check if logger is already created
        self.logger.debug("Moodle Bot {} delete...".format(str(self.bot_id)))
        if hasattr(self, 'logger'):
            handlers = self.logger.handlers[:]
            for handler in handlers:
                handler.close()
                self.logger.removeHandler(handler)

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
                self.sskey = self.driver.find_element(By.XPATH, "//*[@id=\"page-header\"]/div/div/div/div[2]/div[1]/div/form/input[2]").get_attribute("value")
                self.logger.info("sskey: {}".format(self.sskey))
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

    def make_enrolled_courses_by_timeline_classification_url(self):
        return str("https://moodle2.ntust.edu.tw/lib/ajax/service.php?sesskey={}&info=core_course_get_enrolled_courses_by_timeline_classification".format(self.sskey))

    def get_enrolled_courses_by_timeline_classification(self, state:str):
        
        # 建立 requests session
        session = requests.Session()

        # 設定 cookie
        jar = requests.cookies.RequestsCookieJar()
        for cookie in self.driver.get_cookies():
            jar.set(cookie['name'], cookie['value'], domain=cookie['domain'], path=cookie['path'])
        session.cookies.update(jar)

        # 設定 header
        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "Host": "moodle2.ntust.edu.tw",
            "Origin": "https://moodle2.ntust.edu.tw",
            "Referer": "https://moodle2.ntust.edu.tw/my/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        }
        
        # 設定 payload
        if state == "inprogress":
            payload = [{"index":0,"methodname":"core_course_get_enrolled_courses_by_timeline_classification","args":{"offset":0,"limit":0,"classification":"inprogress","sort":"fullname","customfieldname":"","customfieldvalue":""}}]
        elif state == "past":
            payload = [{"index":0,"methodname":"core_course_get_enrolled_courses_by_timeline_classification","args":{"offset":0,"limit":0,"classification":"past","sort":"fullname","customfieldname":"","customfieldvalue":""}}]

        json_payload = json.dumps(payload)

        # debug
        self.logger.debug("url:\n {}".format(self.make_enrolled_courses_by_timeline_classification_url()))
        self.logger.debug("cookies:\n {}".format(session.cookies))
        self.logger.debug("headers:\n {}".format(headers))
        self.logger.debug("payload:\n {}".format(payload))
        
        # 建立課程列表
        course_list = []

        try:
            # 發送請求
            response = session.post(url=self.make_enrolled_courses_by_timeline_classification_url(), headers=headers, data=json_payload)

            # 把回傳text 轉成 json
            data = json.loads(response.text)

            # 拆解原生資料 在包裝成自己的資料
            for course in data[0]["data"]["courses"]:
                
                id = course["id"]
                course_category = course["coursecategory"]
                department = course["summary"]
                fullname = course["fullname"]
                course_id = course["idnumber"]
                startdate = time.strftime("%Y-%m-%d", time.localtime(course["startdate"]))
                enddate = time.strftime("%Y-%m-%d", time.localtime(course["enddate"]))
                viewurl = course["viewurl"]
                has_progress = course["hasprogress"]
                progress = course["progress"]

                single_course = { "id" : id ,
                                  "course_category" : course_category ,
                                  "department" : department ,
                                  "fullname" : fullname ,
                                  "course_id" : course_id ,
                                  "startdate" : startdate ,
                                  "enddate" : enddate ,
                                  "viewurl" : viewurl ,
                                  "hasprogress" : has_progress ,
                                  "progress" : progress
                                }
                course_list.append(single_course)
                for key in single_course:
                    self.logger.debug("{}: {}".format(key, single_course[key]))

        except json.decoder.JSONDecodeError as e:
            self.logger.warning(str(e))
            return False, None

        except Exception as e:
            self.logger.warning(str(e))
            return False, None
        
        return True, course_list


# def test():
#     bot = MoodleBot("b10915003", "A9%t376149", 1)
#     bot.login()
#     bot.get_enrolled_courses_by_timeline_classification()
#     input("Press Enter to continue...")
# test()