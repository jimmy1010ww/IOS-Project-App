import os
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

moodle_logger = logging.getLogger('moodle')
moodle_logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
moodle_logger.addHandler(console_handler)

formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
console_handler.formatter = formatter
console_handler.setLevel(logging.DEBUG)

chrome_options = Options() 
# chrome_options.add_argument('--headless')  # 啟動Headless 無頭
chrome_options.add_argument('--disable-gpu') #關閉GPU 避免某些系統或是網頁出錯
chrome_options.add_argument('--log-level=2') #INFO = 0 WARNING = 1 LOG_ERROR = 2 LOG_FATAL = 3 default = 0
chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])


service = Service(executable_path= os.path.abspath("\driver\chromedriver"))
driver = webdriver.Chrome(service=service, options=chrome_options)

login_url = 'https://moodle2.ntust.edu.tw/login/index.php'
home_page_url = 'https://moodle2.ntust.edu.tw/my/'
driver.get(login_url)

# Find the email and password fields
email_field = driver.find_element(By.ID, "username")
password_field = driver.find_element(By.ID, "password")
login_button = driver.find_element(By.ID, "loginbtn")

# Enter login credentials
email_field.send_keys("b10915003")
password_field.send_keys("A9%t376149")

login_button.click()

try:
    driver.implicitly_wait(5)

    # look if ther have the login error element
    if driver.current_url == login_url:
        moodle_logger.warning("login url is the same\n")
        login_error_element = driver.find_element(By.XPATH, "//*[@id=\"region-main\"]/div/div[3]/div/div[1]/div")
        moodle_logger.warning(login_error_element.text)
    elif (driver.current_url == home_page_url):
        moodle_logger.info("login success\n")
        
except Exception as e:
    moodle_logger.warning(str(e))
    moodle_logger.warning("Timeout")
    try:
        if driver.current_url == login_url:
            moodle_logger.warning("login url is the same\n")
            login_error_element = driver.find_element(By.XPATH, "//*[@id=\"region-main\"]/div/div[3]/div/div[1]/div")
            moodle_logger.warning(login_error_element.text)
    except Exception as e:
        moodle_logger.warning(str(e))
        moodle_logger.critical("Unexpeted error")

input("Press Enter to continue...")


