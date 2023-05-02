import os
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

class MoodleBot:
    def __init__(self):
        self.logger = logging.getLogger('moodle')
        self.logger.setLevel(logging.DEBUG)
        console_handler = logging.StreamHandler()
        self.logger.addHandler(console_handler)

        formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        console_handler.formatter = formatter
        console_handler.setLevel(logging.DEBUG)

        chrome_options = Options() 
        # chrome_options.add_argument('--headless')  # 啟動Headless 無頭
        chrome_options.add_argument('--disable-gpu') #關閉GPU 避免某些系統或是網頁出錯
        chrome_options.add_argument('--log-level=2') #INFO = 0 WARNING = 1 LOG_ERROR = 2 LOG_FATAL = 3 default = 0
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])

        service = Service(executable_path= os.path.abspath("\driver\chromedriver"))
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

    def login(self, email, password):
        login_url = 'https://moodle2.ntust.edu.tw/login/index.php'
        home_page_url = 'https://moodle2.ntust.edu.tw/my/'
        self.driver.get(login_url)

        # Find the email and password fields
        email_field = self.driver.find_element(By.ID, "username")
        password_field = self.driver.find_element(By.ID, "password")
        login_button = self.driver.find_element(By.ID, "loginbtn")

        # Enter login credentials
        email_field.send_keys(email)
        password_field.send_keys(password)

        login_button.click()

        try:
            self.driver.implicitly_wait(5)

            # look if there is a login error element
            if self.driver.current_url == login_url:
                self.logger.warning("login url is the same\n")
                login_error_element = self.driver.find_element(By.XPATH, "//*[@id=\"region-main\"]/div/div[3]/div/div[1]/div")
                self.logger.warning(login_error_element.text)
                return False
            elif self.driver.current_url == home_page_url:
                self.logger.info("login success\n")
                return True

        except Exception as e:
            self.logger.warning(str(e))
            self.logger.warning("Timeout")
            try:
                if self.driver.current_url == login_url:
                    self.logger.warning("login url is the same\n")
                    login_error_element = self.driver.find_element(By.XPATH, "//*[@id=\"region-main\"]/div/div[3]/div/div[1]/div")
                    self.logger.warning(login_error_element.text)
                    return False
            except Exception as e:
                self.logger.warning(str(e))
                self.logger.critical("Unexpeted error")
                return False

    def close(self):
        self.driver.quit()
