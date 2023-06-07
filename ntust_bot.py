import os
import logging
import colorlog
import requests
import time
import pandas as pd
# from seleniumwire import webdriver
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import moodle_bot_exception

class Ntust_bot:
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
        self.logger = logging.getLogger('Ntust_{}'.format(str(self.bot_id)))
        # set logger level
        self.logger.setLevel(logging.DEBUG)
        # create formatter
        formatter = colorlog.ColoredFormatter(
            '[Ntust Bot Logger] %(asctime)s %(log_color)s%(levelname)-8s%(reset)s %(message)s',
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

        self.logger.debug("Ntust Bot {} init...".format(str(self.bot_id)))
        self.logger.debug("username : {} password: {}".format(str(self.username), str(self.password)))
        self.initDriver()
        self.logger.info("Ntust Bot {} init done".format(str(self.bot_id)))

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
        self.logger.debug("Ntust Bot {} delete...".format(str(self.bot_id)))
        if hasattr(self, 'logger'):
            handlers = self.logger.handlers[:]
            for handler in handlers:
                handler.close()
                self.logger.removeHandler(handler)

    def login(self):
        login_url = 'https://stuinfosys.ntust.edu.tw/StuScoreQueryServ/StuScoreQuery'

        self.logger.debug("login")

        self.driver.get(login_url)

        self.logger.debug(self.driver.current_url)

        # Find the email and password fields
        email_field = self.driver.find_element(By.ID, "Ecom_User_ID")
        password_field = self.driver.find_element(By.ID, "Ecom_Password")
        login_button = self.driver.find_element(By.ID, "loginButton2")

        # Enter login credentials
        for word in self.username:
            email_field.send_keys(word)
            time.sleep(0.3)  # wait for 0.3 seconds

        for word in self.password:
            password_field.send_keys(word)
            time.sleep(0.3)  # wait for 0.3 seconds

        # Click the login button
        login_button.click()
        input("Press Enter to continue...")
        return True
    
    def close(self):
        self.driver.quit()

    def getScore(self):
        # self.driver.save_screenshot('screenshot.png')
        show_score_button = self.driver.find_element(By.ID, "DisplayAll")
        show_score_button.click()

        # get the html page source
        page = self.driver.page_source
        # Parse the HTML with BeautifulSoup
        soup = BeautifulSoup(page, 'html.parser')

        # Find the table in the soup
        table = soup.find('table')

        # Read the table into a pandas DataFrame
        data = pd.read_html(str(table))[0]

        dict_data = data.to_dict('records')
        
        return True, dict_data
    
    def getCourseTable(self):
        login_url = 'https://stuinfosys.ntust.edu.tw/NTUSTSSOServ/SSO/Login/CourseSelection?ReturnUrl=CourseSelection'

        self.logger.debug("login")

        self.driver.get(login_url)

        self.logger.debug(self.driver.current_url)

        actions = ActionChains(self.driver)

        # Find the email and password fields
        email_field = self.driver.find_element(By.NAME, "UserName")
        password_field = self.driver.find_element(By.NAME, "Password")
        login_button = self.driver.find_element(By.ID, "btnLogIn")

        # Enter login credentials
        actions.move_to_element(email_field).click().perform()

        email_field.send_keys(self.username)

        actions.move_to_element(password_field).click().perform()
            
        password_field.send_keys(self.password)


        
        actions.move_to_element(login_button).click().perform()

        # wait for the page to load
        try:
            input("Press Enter to continue...")

            # look if there is a login error element
            if self.driver.current_url == login_url:
                self.logger.info("Login Success")
                # self.sskey = self.driver.find_element(By.XPATH, "//*[@id=\"page-header\"]/div/div/div/div[2]/div[1]/div/form/input[2]").get_attribute("value")
                # self.logger.info("sskey: {}".format(self.sskey))

            elif self.driver.current_url != login_url:
                self.logger.warning("login url is the same")
                # login_error_element = self.driver.find_element(By.XPATH, "//*[@id=\"region-main\"]/div/div[3]/div/div[1]/div")
                # self.logger.warning(login_error_element.text)


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
        
        courese_toggle_list = self.driver.find_element(By.XPATH, "//*[@id=\"navigation\"]/ul[1]/li[4]/a")
        courese_toggle_list.click()

        course_table_button = self.driver.find_element(By.XPATH, "//*[@id=\"navigation\"]/ul[1]/li[4]/ul/li[1]/a")
        course_table_button.click()

        # get the html page source
        page = self.driver.page_source

        soup = BeautifulSoup(page, 'html.parser')


        # 找到表格元素
        table = soup.find_all('table')

        # 抓取表個資料
        data = []
        table_index = 3  # 抓取第四個表格
        header_row = table[table_index].find('tr')  # 標題列
        header_columns = header_row.find_all('td')  # 標題行
        header = [cell.get_text(strip=True) for cell in header_columns]

        # 跳過標題列
        rows = table[table_index].find_all('tr')[1:]

        for row in rows:
            row_data = {}
            cells = row.find_all('td')
            if cells:  # 确保该行不是空行
                for i, cell in enumerate(cells):
                    cell_text = cell.get_text(strip=True).replace('\n', '').replace(' ', '')  # 去除换行符号和空格
                    row_data[header[i]] = cell_text
                data.append(row_data)

        return True, data
    