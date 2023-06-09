
import logging
import colorlog
from flask import Flask, render_template, request as flask_request
from flask import jsonify
from moodle_bot import MoodleBot
from ntust_bot import Ntust_bot
from app_json_parameter import app_json_parameter as json_parameter
import app_sever_exception as server_exception

app = Flask(__name__)
# 這個應用程式會創建一個 Flask 實例，並將 /hello 網址綁定到 hello() 函數。
# 當使用 GET 請求訪問 /hello 時，如果指定了 name 參數，它將使用該參數來回應訊息。如果未指定 name 參數，則使用 "World" 作為預設值。
#當使用 POST 請求訪問 /hello 時，它將從請求表單中獲取 name 參數並回應訊息。

flask_logger = logging.getLogger('flask')
flask_logger.setLevel(logging.DEBUG)
formatter = colorlog.ColoredFormatter(
            '[Flask Logger] %(asctime)s %(log_color)s%(levelname)-8s%(reset)s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )
console_handler = logging.StreamHandler()
console_handler.formatter = formatter
console_handler.setLevel(logging.DEBUG)
flask_logger.addHandler(console_handler)


ntustBot_list = []
moodleBot_list = []
ntustBot_userid_list = []
moodleBot_userid_list = []

# 取得處理 exception 的 json return
def get_exception_json_return(_message):
    return_json = jsonify({json_parameter.RESULT: json_parameter.RESULT_FAILED, json_parameter.MESSAGE: _message})
    flask_logger.info("Return Json : {}".format(return_json))
    return return_json

# 取得回傳 sucess 的 json return
def get_success_json_return(_message):
    return_json = jsonify({json_parameter.RESULT: json_parameter.RESULT_SUCCESS, json_parameter.MESSAGE: _message})
    flask_logger.info("Return Json : {}".format(return_json))
    return return_json

# 處理 exception 的 message
def handle_exception_message(_message):
    flask_logger.error(_message)

# 處理 success 的 message
def handle_success_message(_message):
    flask_logger.info(_message)

# 印出 Client IP 和 Port 到 logger
def logger_print_client_info(_request):
    flask_logger.info("Client IP : {}".format(str(_request.remote_addr)))
    flask_logger.info("Clinet Port : {}".format(str(_request.environ['REMOTE_PORT'])))

# 產生新的 moodleBot userid
def generate_moodleBot_userid():
    if moodleBot_userid_list == []:
        moodleBot_userid_list.append(0)
    else:   
        moodleBot_userid_list.append(moodleBot_userid_list[-1]+1)
    return moodleBot_userid_list[-1]

# 產生新的 ntustBot userid
def generate_ntustBot_userid():
    if ntustBot_userid_list == []:
        ntustBot_userid_list.append(0)
    else:   
        ntustBot_userid_list.append(ntustBot_userid_list[-1]+1)
    return ntustBot_userid_list[-1]

# 檢查 userid 是否存在
def check_userid_exist(_userid, type):
    # check moodleBot userid
    if type == 0:
        if _userid in moodleBot_userid_list:
            return True
    elif type == 1:
        if _userid in ntustBot_userid_list:
            return True
    else:
        return False

# 檢查 post data 是否為空
def check_receive_data(_request):
    data = _request.get_json()
    if data != None:
        return True, data
    else:
        return False, None

@app.route('/test', methods=['GET'])
def test():
    try:
        if flask_request.method == 'GET':
            flask_logger.debug("[GET] /test")
            
            current_moodle_bot = MoodleBot("B10915003", "A9%t376149", 0, headless=False)

            current_moodle_bot.login()

            ret, data = current_moodle_bot.get_calendar_monthly(2023,4)
            if ret:
                return_data_list = {json_parameter.RESULT: json_parameter.RESULT_SUCCESS, json_parameter.DATA: data }
                return jsonify(return_data_list)
            else:
                raise server_exception.MoodleBotError("Get courses failed")
        else :
            raise server_exception.InvalidRequestMethod()
    except server_exception.InvalidRequestMethod as e:
        flask_logger.warning(str(e))
        return get_exception_json_return(str(e))
    except Exception as e:
        handle_exception_message(str(e))
        return get_exception_json_return(str(e))
    
    
    
# 提供 client 打招呼確認 server 是否正常運作
@app.route('/hello', methods=['GET', 'POST'])
def hello():
    try:
        if flask_request.method == 'GET':
            flask_logger.debug("[GET] /hello")
            return get_success_json_return("Hello USER!")
        else :
            raise server_exception.InvalidRequestMethod()
    except server_exception.InvalidRequestMethod as e:
        flask_logger.warning(str(e))
        return get_exception_json_return(str(e))
    except Exception as e:
        handle_exception_message(str(e))
        return get_exception_json_return(str(e))
    
# 讓 client 檢查 moodlebot userid 是否存在
@app.route('/api/check_moodleBot_userid', methods=['POST'])
def check_moodleBot_userid():
    try:
        if flask_request == 'POST':
            flask_logger.debug("[POST] /api/check_moodleBot_userid")

            # 印出Clien IP和Port
            logger_print_client_info(flask_request)

            # 取的 post data 並且檢查
            is_received, data = check_receive_data(flask_request)

            if not is_received:
                raise server_exception.InvalidReceiveData("Data is None!")

            # 檢查 userid 是否存在
            if check_userid_exist(data[json_parameter.USERID], 0):
                return get_success_json_return("Userid: {} exist!".format(data[json_parameter.USERID]))
            else:
                raise server_exception.UserIDNotExist(data[json_parameter.USERID])
        else:
            raise server_exception.UserIDNotExist()
    
    except server_exception.UserIDNotExist as e:
        flask_logger.warning(str(e))
        return get_exception_json_return(str(e))
    except server_exception.InvalidRequestMethod as e:
        flask_logger.warning(str(e))
        return get_exception_json_return(str(e))
    except server_exception.InvalidReceiveData as e:
        flask_logger.warning(str(e))
        return get_exception_json_return(str(e))
    except Exception as e:
        handle_exception_message(str(e))
        return get_exception_json_return(str(e))

# 讓 client 檢查 ntustBot userid 是否存在
@app.route('/api/check_ntustBot_userid', methods=['POST'])
def check_ntustBot_userid():
    try:
        if flask_request == 'POST':
            flask_logger.debug("[POST] /api/check_ntustBot_userid")

            # 印出Clien IP和Port
            logger_print_client_info(flask_request)

            # 取的 post data 並且檢查
            is_received, data = check_receive_data(flask_request)

            if not is_received:
                raise server_exception.InvalidReceiveData("Data is None!")

            # 檢查 userid 是否存在
            if check_userid_exist(data[json_parameter.USERID], 1):
                return get_success_json_return("Userid: {} exist!".format(data[json_parameter.USERID]))
            else:
                raise server_exception.UserIDNotExist(data[json_parameter.USERID])
        else:
            raise server_exception.UserIDNotExist()
    
    except server_exception.UserIDNotExist as e:
        flask_logger.warning(str(e))
        return get_exception_json_return(str(e))
    except server_exception.InvalidRequestMethod as e:
        flask_logger.warning(str(e))
        return get_exception_json_return(str(e))
    except server_exception.InvalidReceiveData as e:
        flask_logger.warning(str(e))
        return get_exception_json_return(str(e))
    except Exception as e:
        handle_exception_message(str(e))
        return get_exception_json_return(str(e))

# 檢查 moodle系統 是否可以登入
@app.route('/api/check_moodle_login', methods=['POST'])
def check_moodle_login():
    try: 
        #如果是POST請求，從請求獲取json來進行登入
        if flask_request.method == 'POST':
            flask_logger.debug("[POST] /api/check_moodle_login]")
            
            #印出Clien IP和Port
            logger_print_client_info(flask_request)

            #從請求獲取json
            is_received, data = check_receive_data(flask_request)

            if not is_received:
                raise server_exception.InvalidReceiveData("Data is None!")

            #從json中獲取帳號密碼
            username = data[json_parameter.USERNAME]
            password = data[json_parameter.PASSWORD]
            flask_logger.info("username : {} password: {}".format(str(username), str(password)))
            
            # 產生新的 userid
            current_userid = generate_moodleBot_userid()

            #宣告moodleLogin物件
            current_moodleBot = MoodleBot(username, password, current_userid, headless=True)
            
            #如果登入成功，回傳json
            if current_moodleBot.login():
                flask_logger.info("Login Success")
                flask_logger.info("userid : {}".format(str(current_moodleBot.bot_id)))
                flask_logger.debug("moodleBot_list length : {}".format(str(len(moodleBot_list))))

                # 登入成功，新增 moodleBot 物件到 moodleBot_list
                moodleBot_list.append(current_moodleBot)
                return_data = jsonify({json_parameter.RESULT: json_parameter.RESULT_SUCCESS, json_parameter.USERID: current_moodleBot.bot_id})
                flask_logger.debug("return_data : {}".format(return_data.json))
                return return_data
            else:
                moodleBot_userid_list.remove(moodleBot_userid_list[-1])
                flask_logger.warning("Login Failed")
                flask_logger.debug("moodleBot_list length : {}".format(str(len(moodleBot_list))))
                return get_exception_json_return("Login Failed")
        #如果不是POST請求，回傳錯誤
        else:
            raise server_exception.InvalidRequestMethod()
    
    except server_exception.InvalidRequestMethod as e:
        flask_logger.warning(str(e))
        return get_exception_json_return(str(e))
    except server_exception.InvalidReceiveData as e:
        flask_logger.warning(str(e))
        return get_exception_json_return(str(e))
    except Exception as e:
        handle_exception_message(str(e))
        return get_exception_json_return(str(e))

# 取得 moodle 的課程資訊    
@app.route('/api/get_courses', methods=['POST'])
def get_courses():
    try:
        if flask_request.method == 'POST':
            #印出請求方式
            flask_logger.debug("[POST] /api/get_courses")
            
            #印出Clien IP和Port
            logger_print_client_info(flask_request)

            #從請求獲取json
            is_received, data = check_receive_data(flask_request)
            if not is_received:
                raise server_exception.InvalidReceiveData("Data is None!")
            
            # 讀取 post data
            userid = int(data[json_parameter.USERID])
            classification = data[json_parameter.CLASSIFICATION]
            sort = data[json_parameter.SORT]

            # 檢查 post data
            if classification not in ['past', 'inprogress']:
                raise server_exception.InvalidPostParameter("classification value error")
            elif sort not in ['fullname', 'ul.timeaccess desc']:
                return server_exception.InvalidPostParameter("sort value error")

            # 檢查 userid 是否存在
            if not check_userid_exist(userid, 0):
                raise server_exception.UserIDNotExist(userid)
            
            # 取得 moodleBot 物件
            current_moodleBot = moodleBot_list[userid]

            # 取得課程資訊
            ret, course_list = current_moodleBot.get_enrolled_courses_by_timeline_classification(classification=classification, sort=sort)

            # 建立回傳的 json list
            return_data_list = []
            
            # 如果成功取得課程資訊
            if ret:
                return_data_list = {json_parameter.RESULT: json_parameter.RESULT_SUCCESS, json_parameter.DATA: course_list }
                return jsonify(return_data_list)
            else:
                raise server_exception.MoodleBotError("Get courses failed")
    except server_exception.MoodleBotError as e:
        flask_logger.critical(str(e))
        return get_exception_json_return(str(e))            
    except server_exception.UserIDNotExist as e:
        flask_logger.warning(str(e))
        return get_exception_json_return(str(e))
    except server_exception.InvalidRequestMethod as e:
        flask_logger.warning(str(e))
        return get_exception_json_return(str(e))
    except server_exception.InvalidReceiveData as e:
        flask_logger.warning(str(e))
        return get_exception_json_return(str(e))
    except server_exception.InvalidPostParameter as e:
        flask_logger.warning(str(e))
        return get_exception_json_return(str(e))
    except Exception as e:
        handle_exception_message(str(e))
        return get_exception_json_return(str(e))

# 取得 moodle 課程的頁面資訊
@app.route('/api/get_course_page', methods=['POST'])
def get_course_page():
    try:
        if flask_request.method == 'POST':
            flask_logger.debug("[POST] /api/get_course_page")

            #印出Clien IP和Port
            logger_print_client_info(flask_request)

            #從請求獲取json
            is_received, data = check_receive_data(flask_request)
            if not is_received:
                raise server_exception.InvalidReceiveData("Data is None!")
            
            # 讀取 post data
            userid = int(data['userid'])
            courseid = int(data['courseid'])

            # 檢查 userid 是否存在
            if not check_userid_exist(userid, 0):
                raise server_exception.UserIDNotExist(userid)
            
            # 取得 moodleBot 物件
            current_moodleBot = moodleBot_list[userid]

            # 取得單個課程頁面
            ret, data = current_moodleBot.get_course_page(courseid)

            if ret:
                return_data = {json_parameter.RESULT: json_parameter.RESULT_SUCCESS, json_parameter.COURSEID: courseid, json_parameter.DATA: data}
                return jsonify(return_data)
        else:
            raise server_exception.InvalidRequestMethod()
    except server_exception.MoodleBotError as e:
        flask_logger.critical(str(e))
        return get_exception_json_return(str(e))            
    except server_exception.UserIDNotExist as e:
        flask_logger.warning(str(e))
        return get_exception_json_return(str(e))
    except server_exception.InvalidRequestMethod as e:
        flask_logger.warning(str(e))
        return get_exception_json_return(str(e))
    except server_exception.InvalidReceiveData as e:
        flask_logger.warning(str(e))
        return get_exception_json_return(str(e))
    except server_exception.InvalidPostParameter as e:
        flask_logger.warning(str(e))
        return get_exception_json_return(str(e))
    except Exception as e:
        flask_logger.error(str(e))
        return get_exception_json_return(str(e))

# 取得 moodle 的日曆資訊
@app.route('/api/get_calendar', methods=['POST'])
def get_calendar():
    try:
        if flask_request.method == 'POST':
            flask_logger.debug("[POST] /api/get_calendar")

            #印出Clien IP和Port
            logger_print_client_info(flask_request)

            #從請求獲取json
            is_received, data = check_receive_data(flask_request)
            if not is_received:
                raise server_exception.InvalidReceiveData("Data is None!")
            
            # 讀取 post data
            userid = int(data['userid'])
            year =  int(data['year'])
            month = int(data['month'])
            

            # 檢查 userid 是否存在
            if not check_userid_exist(userid, 0):
                raise server_exception.UserIDNotExist(userid)
            
            # 取得 moodleBot 物件
            current_moodleBot = moodleBot_list[userid]

            # 取得單個課程頁面
            ret, data = current_moodleBot.get_calendar_monthly(year, month)

            if ret:
                return_data = {json_parameter.RESULT: json_parameter.RESULT_SUCCESS, json_parameter.DATA: data}
                return jsonify(return_data)
        else:
            raise server_exception.InvalidRequestMethod()
    except server_exception.MoodleBotError as e:
        flask_logger.critical(str(e))
        return get_exception_json_return(str(e))            
    except server_exception.UserIDNotExist as e:
        flask_logger.warning(str(e))
        return get_exception_json_return(str(e))
    except server_exception.InvalidRequestMethod as e:
        flask_logger.warning(str(e))
        return get_exception_json_return(str(e))
    except server_exception.InvalidReceiveData as e:
        flask_logger.warning(str(e))
        return get_exception_json_return(str(e))
    except server_exception.InvalidPostParameter as e:
        flask_logger.warning(str(e))
        return get_exception_json_return(str(e))
    except Exception as e:
        flask_logger.error(str(e))
        return get_exception_json_return(str(e))

# 檢查 Ntust系統 是否可以登入
@app.route('/api/check_ntust_login', methods=['POST'])
def check_ntust_login():
    try: 
        #如果是POST請求，從請求獲取json來進行登入
        if flask_request.method == 'POST':
            flask_logger.debug("[POST] /api/check_ntust_login]")
            
            #印出Clien IP和Port
            logger_print_client_info(flask_request)

            #從請求獲取json
            is_received, data = check_receive_data(flask_request)

            if not is_received:
                raise server_exception.InvalidReceiveData("Data is None!")

            #從json中獲取帳號密碼
            username = data[json_parameter.USERNAME]
            password = data[json_parameter.PASSWORD]
            flask_logger.info("username : {} password: {}".format(str(username), str(password)))
            
            # 產生新的 userid
            current_userid = generate_ntustBot_userid()

            #宣告 nutust_bot 物件
            current_ntust_bot = Ntust_bot(username, password, current_userid, headless=False)
            
            #如果登入成功，回傳json
            if current_ntust_bot.login():
                flask_logger.info("Login Success")
                flask_logger.info("userid : {}".format(str(current_ntust_bot.bot_id)))
                flask_logger.debug("ntustBot_list length : {}".format(str(len(ntustBot_list))))

                # 登入成功，新增 ntustBot 物件到 ntustBot_list
                ntustBot_list.append(current_ntust_bot)
                return_data = jsonify({json_parameter.RESULT: json_parameter.RESULT_SUCCESS, json_parameter.USERID: current_ntust_bot.bot_id})
                flask_logger.debug("return_data : {}".format(return_data.json))
                return return_data
            else:
                ntustBot_userid_list.remove(ntustBot_userid_list[-1])
                flask_logger.warning("Login Failed")
                flask_logger.debug("ntustBot_list length : {}".format(str(len(ntustBot_list))))
                return get_exception_json_return("Login Failed")
        #如果不是POST請求，回傳錯誤
        else:
            raise server_exception.InvalidRequestMethod()
    
    except server_exception.InvalidRequestMethod as e:
        flask_logger.warning(str(e))
        return get_exception_json_return(str(e))
    except server_exception.InvalidReceiveData as e:
        flask_logger.warning(str(e))
        return get_exception_json_return(str(e))
    except Exception as e:
        handle_exception_message(str(e))
        return get_exception_json_return(str(e))

# 取得 Ntust的歷年成績
@app.route('/api/get_ntust_score', methods=['POST'])
def get_ntust_score():
    try:
        if flask_request.method == 'POST':
            flask_logger.debug("[POST] /api/get_ntust_score")

            #印出Clien IP和Port
            logger_print_client_info(flask_request)

            #從請求獲取json
            is_received, data = check_receive_data(flask_request)
            if not is_received:
                raise server_exception.InvalidReceiveData("Data is None!")
            
            # 讀取 post data
            userid = int(data['userid'])

            # 檢查 userid 是否存在
            if not check_userid_exist(userid, 1):
                raise server_exception.UserIDNotExist(userid)
            
            # 取得 ntust_bot 物件
            current_ntustBot = ntustBot_list[userid]

            # 取得單個課程頁面
            ret, data = current_ntustBot.getScore()

            if ret:
                return_data = {json_parameter.RESULT: json_parameter.RESULT_SUCCESS, json_parameter.DATA: data}
                return jsonify(return_data)
        else:
            raise server_exception.InvalidRequestMethod()
    except server_exception.MoodleBotError as e:
        flask_logger.critical(str(e))
        return get_exception_json_return(str(e))            
    except server_exception.UserIDNotExist as e:
        flask_logger.warning(str(e))
        return get_exception_json_return(str(e))
    except server_exception.InvalidRequestMethod as e:
        flask_logger.warning(str(e))
        return get_exception_json_return(str(e))
    except server_exception.InvalidReceiveData as e:
        flask_logger.warning(str(e))
        return get_exception_json_return(str(e))
    except server_exception.InvalidPostParameter as e:
        flask_logger.warning(str(e))
        return get_exception_json_return(str(e))
    except Exception as e:
        flask_logger.error(str(e))
        return get_exception_json_return(str(e))

# 取得 Ntust課表
@app.route('/api/get_course_table', methods=['POST'])
def get_course_table():
    try:
        if flask_request.method == 'POST':
            flask_logger.debug("[POST] /api/get_course_table")

            #印出Clien IP和Port
            logger_print_client_info(flask_request)

            #從請求獲取json
            is_received, data = check_receive_data(flask_request)
            if not is_received:
                raise server_exception.InvalidReceiveData("Data is None!")
            
            # 讀取 post data
            userid = int(data['userid'])

            # 檢查 userid 是否存在
            if not check_userid_exist(userid, 1):
                raise server_exception.UserIDNotExist(userid)
            
            
            # 取得 ntust_bot 物件
            current_ntustBot = ntustBot_list[userid]

            # 取得單個課程頁面
            ret, data = current_ntustBot.getCourseTable()

            if ret:
                return_data = {json_parameter.RESULT: json_parameter.RESULT_SUCCESS, json_parameter.DATA: data}
                return jsonify(return_data)
        else:
            raise server_exception.InvalidRequestMethod()
    except server_exception.MoodleBotError as e:
        flask_logger.critical(str(e))
        return get_exception_json_return(str(e))            
    except server_exception.UserIDNotExist as e:
        flask_logger.warning(str(e))
        return get_exception_json_return(str(e))
    except server_exception.InvalidRequestMethod as e:
        flask_logger.warning(str(e))
        return get_exception_json_return(str(e))
    except server_exception.InvalidReceiveData as e:
        flask_logger.warning(str(e))
        return get_exception_json_return(str(e))
    except server_exception.InvalidPostParameter as e:
        flask_logger.warning(str(e))
        return get_exception_json_return(str(e))
    except Exception as e:
        flask_logger.error(str(e))
        return get_exception_json_return(str(e))

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)