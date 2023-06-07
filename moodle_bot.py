import os
import logging
import colorlog
import requests
import json
import re
import time
import lxml
# from seleniumwire import webdriver
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import moodle_bot_exception

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
        self.session = requests.session()
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

    def set_session_cookie(self):
        # 設定 cookie
        jar = requests.cookies.RequestsCookieJar()
        for cookie in self.driver.get_cookies():
            jar.set(cookie['name'], cookie['value'], domain=cookie['domain'], path=cookie['path'])
        self.session.cookies.update(jar)

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
    
    def make_course_page_url(self, course_id:int):
        return str("https://moodle2.ntust.edu.tw/course/view.php?id={}".format(course_id))
    
    def make_calendar_monthly_view_url(self):
        return  str("https://moodle2.ntust.edu.tw/lib/ajax/service.php?sesskey={}&info=core_calendar_get_calendar_monthly_view".format(self.sskey))

    def check_response_valid(self, response:list):
        try:
            self.logger.info(response[0]['error'])
            if response[0]['error'] == False:
                return True
            else:
                error_code = response[0]['exception']['errorcode']
                if error_code == "servicerequireslogin":
                    raise moodle_bot_exception.MoodleCookiesError()
                elif error_code == "invalidsesskey":
                    raise moodle_bot_exception.MoodleSskeyError()
        except:
            self.logger.warning("response error")
            self.logger.info("login again")
            if self.login():
                return True
            else:
                return False

    def check_calendar_valid(self, response:list):
        try:
            self.logger.info(type(response[0]['error']))
            if response[0]['error'] == False:
                return True
            else:
                error_code = response[0]['exception']['errorcode']
                if error_code == "servicerequireslogin":
                    raise moodle_bot_exception.MoodleCookiesError()
                elif error_code == "invalidsesskey":
                    raise moodle_bot_exception.MoodleSskeyError()
        except:
            self.logger.warning("response error")
            self.logger.info("login again")
            if self.login():
                return True
            else:
                return False

    def get_enrolled_courses_by_timeline_classification(self, classification:str = "inprogress", sort:str = "fullname"):
        try:
            self.set_session_cookie()

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
            payload = [{"index":0,"methodname":"core_course_get_enrolled_courses_by_timeline_classification","args":{"offset":0,"limit":0,"classification":classification,"sort":sort,"customfieldname":"","customfieldvalue":""}}]

            json_payload = json.dumps(payload)

            # debug
            self.logger.debug("url:\n {}".format(self.make_enrolled_courses_by_timeline_classification_url()))
            self.logger.debug("cookies:\n {}".format(self.session.cookies))
            self.logger.debug("headers:\n {}".format(headers))
            self.logger.debug("payload:\n {}".format(payload))
            
            # 建立課程列表
            course_list = []

            # 發送請求
            response = self.session.post(url=self.make_enrolled_courses_by_timeline_classification_url(), headers=headers, data=json_payload)

            if not self.check_response_valid(response.json()):
                raise moodle_bot_exception.MoodleLoginError()
            
            # 把回傳text 轉成 json
            data = json.loads(response.text)

            # 拆解原生資料 在包裝成自己的資料
            for course in data[0]["data"]["courses"]:

                # 利用　正規表達式　從 fullname 中取出系所名稱
                match = re.search(r"\【(.+?)\】", course["fullname"])
                if match:
                    content = match.group(1)
                else:
                    raise moodle_bot_exception.MoodleResponseError("Can't find department name in fullname")
                
                # 把資料包裝成自己的格式
                id = course["id"]
                course_category = course["coursecategory"]
                department = str(content)
                fullname = course["fullname"]
                course_id = course["idnumber"]
                startdate = time.strftime("%Y-%m-%d", time.localtime(course["startdate"]))
                enddate = time.strftime("%Y-%m-%d", time.localtime(course["enddate"]))
                viewurl = course["viewurl"]
                has_progress = course["hasprogress"]
                progress = course["progress"]

                # 創建 single course dict
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
                
                # 把 sigle course dict 加入 list
                course_list.append(single_course)
                for key in single_course:
                    self.logger.info("{}: {}".format(key, single_course[key]))
            return True, course_list
        except json.decoder.JSONDecodeError as e:
                self.logger.warning(str(e))
                return False, None
        except moodle_bot_exception.MoodleLoginError as e:
            self.logger.error(str(e))
            return False, None
        except Exception as e:
            self.logger.warning(str(e))
            return False, None

    def get_course_page(self, course_id:int):
        try:
            # 設定 session cookie
            self.set_session_cookie()

            return_json_data = {
                "week_list" : []
            }

            # 設定 header
            headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                "Connection": "keep-alive",
                "Host": "moodle2.ntust.edu.tw",
                "Referer": "https://moodle2.ntust.edu.tw/my/",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
            }

            response = self.session.get(url=self.make_course_page_url(course_id), headers=headers)
            
            # bs4 解析
            # 解析內容 (轉為string)
            content = response.content.decode()
            soup = BeautifulSoup(content, 'html.parser')
            
            for li in soup.find('ul', class_='weeks').find_all('li', class_ = 'section main clearfix'):
                
                single_week = {
                    "week" : "",
                    "section" : []
                }

                content = li.find('div', class_='content')
                current_week = content.find('h3').find('span').text
                self.logger.info("WEEK: {}\n".format(current_week))

                single_week["week"] = current_week

                try:
                    section = content.find('ul', class_ = 'section img-text')
                    for item in section:    
                        section_data = {
                            "name" : "",
                            "url" : "",
                            "icon_url" : ""
                        }
                        
                        url = item.find('a')['href']
                        icon_url = item.find('img')['src']
                        name = item.find('span', class_ = 'instancename').text

                        self.logger.info("url: {}".format(url))
                        self.logger.info("icon_url: {}".format(icon_url))
                        self.logger.info("name: {}\n".format(name))


                        # if "mod/assign" in url:
                        #     assignment_data = self.get_assaign_page(url)

                        section_data["name"] = name
                        section_data["url"] = url
                        section_data["icon_url"] = icon_url
                        single_week["section"].append(section_data)
                except Exception as e:
                    self.logger.warning(str(e))
                    single_week["section"].append("None")

                return_json_data["week_list"].append(single_week)
                # self.logger.info("li: {}\n".format(li))

            # for week in return_json_data["data"]:
            #     print('\n')
            #     self.logger.info("week: {}".format(week["week"]))
            #     index = 0
            #     for section in week["section"]:
            #         self.logger.info("{}. ".format(index))
            #         self.logger.info("name: {}".format(section["name"]))
            #         self.logger.info("url: {}".format(section["url"]))
            #         self.logger.info("icon_url: {}".format(section["icon_url"]))
            #         index += 1
            return True, return_json_data
        except Exception as e:
            self.logger.warning(str(e))
            return False, None

    def get_calendar_monthly(self, year:int, month:int):
        try:
            self.set_session_cookie()
            self.session.get(url = "https://moodle2.ntust.edu.tw/calendar/view.php?view=month")
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
            payload = [{"index":0,"methodname":"core_calendar_get_calendar_monthly_view","args":{"year":2023,"month":6,"courseid":1,"categoryid":0,"includenavigation":False,"mini":True,"day":1}}]

            payload = json.dumps(payload).replace('True', 'true').replace('False', 'false')

            # debug
            self.logger.debug("url:\n {}".format(self.make_calendar_monthly_view_url()))
            self.logger.debug("cookies:\n {}".format(self.session.cookies))
            self.logger.debug("headers:\n {}".format(headers))
            self.logger.debug("payload:\n {}".format(payload))
            
            # 建立課程列表
            course_list = []

            # 發送請求
            response = self.session.post(url=self.make_calendar_monthly_view_url(), headers=headers, data=payload)

            self.logger.debug("response:\n {}".format(response.text))

            if not self.check_response_valid(response.json()):
                raise moodle_bot_exception.MoodleLoginError()
            
            # 把回傳text 轉成 json
            data = json.loads(response.text)
            print(data)


            # temp return
            return False, None

            # # 拆解原生資料 在包裝成自己的資料
            # for course in data[0]["data"]["courses"]:

            #     # 利用　正規表達式　從 fullname 中取出系所名稱
            #     match = re.search(r"\【(.+?)\】", course["fullname"])
            #     if match:
            #         content = match.group(1)
            #     else:
            #         raise moodle_bot_exception.MoodleResponseError("Can't find department name in fullname")
                
            #     # 把資料包裝成自己的格式
            #     id = course["id"]
            #     course_category = course["coursecategory"]
            #     department = str(content)
            #     fullname = course["fullname"]
            #     course_id = course["idnumber"]
            #     startdate = time.strftime("%Y-%m-%d", time.localtime(course["startdate"]))
            #     enddate = time.strftime("%Y-%m-%d", time.localtime(course["enddate"]))
            #     viewurl = course["viewurl"]
            #     has_progress = course["hasprogress"]
            #     progress = course["progress"]

            #     # 創建 single course dict
            #     single_course = { "id" : id ,
            #                     "course_category" : course_category ,
            #                     "department" : department ,
            #                     "fullname" : fullname ,
            #                     "course_id" : course_id ,
            #                     "startdate" : startdate ,
            #                     "enddate" : enddate ,
            #                     "viewurl" : viewurl ,
            #                     "hasprogress" : has_progress ,
            #                     "progress" : progress
            #                     }
                
            #     # 把 sigle course dict 加入 list
            #     course_list.append(single_course)
            #     for key in single_course:
            #         self.logger.info("{}: {}".format(key, single_course[key]))
            # return True, course_list
        except json.decoder.JSONDecodeError as e:
                self.logger.warning(str(e))
                return False, None
        except moodle_bot_exception.MoodleLoginError as e:
            self.logger.error(str(e))
            return False, None
        except Exception as e:
            self.logger.warning(str(e))
            return False, None
    