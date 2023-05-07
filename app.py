
import logging
import colorlog
from flask import Flask, render_template, request as flask_request
from flask import jsonify
from moodle_bot import MoodleBot
from post_parameter import PostParameter as post_parameter
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


moodleBot_list = []
userid_list = []

# 取得處理 exception 的 json return
def get_exception_json_return(_message):
    return_json = jsonify({post_parameter.RESULT: post_parameter.RESULT_FAILED, post_parameter.MESSAGE: _message})
    flask_logger.info("Return Json : {}".format(return_json))
    return return_json

# 取得回傳 sucess 的 json return
def get_success_json_return(_message):
    return_json = jsonify({post_parameter.RESULT: post_parameter.RESULT_SUCCESS, post_parameter.MESSAGE: _message})
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

# 產生新的 userid
def generate_userid():
    if userid_list == []:
        userid_list.append(0)
    else:   
        userid_list.append(userid_list[-1]+1)
    return userid_list[-1]

# 檢查 userid 是否存在
def check_userid_exist(_userid):
    if _userid in userid_list:
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
            
            current_moodleBot = MoodleBot("B10915003", "A9%t376149", 0, headless=True)
            current_moodleBot.login()
            current_moodleBot.get_enrolled_courses_by_timeline_classification()
            current_moodleBot.get_course_page(4932)
            return get_success_json_return("Running Test!")
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
    
# 讓 client 檢查 userid 是否存在
@app.route('/api/check_userid', methods=['POST'])
def check_userid():
    try:
        if flask_request == 'POST':
            flask_logger.debug("[POST] /api/check_userid")

            # 印出Clien IP和Port
            logger_print_client_info(flask_request)

            # 取的 post data 並且檢查
            is_received, data = check_receive_data(flask_request)

            if not is_received:
                raise server_exception.InvalidReceiveData("Data is None!")

            # 檢查 userid 是否存在
            if check_userid_exist(data[post_parameter.USERID]):
                return get_success_json_return("Userid: {} exist!".format(data[post_parameter.USERID]))
            else:
                raise server_exception.UserIDNotExist(data[post_parameter.USERID])
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

# 檢查moodle是否可以正確登入
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
            username = data[post_parameter.USERNAME]
            password = data[post_parameter.PASSWORD]
            flask_logger.info("username : {} password: {}".format(str(username), str(password)))
            
            # 產生新的 userid
            current_userid = generate_userid()

            #宣告moodleLogin物件
            current_moodleBot = MoodleBot(username, password, current_userid, headless=False)
            
            #如果登入成功，回傳json
            if current_moodleBot.login():
                flask_logger.info("Login Success")
                flask_logger.info("userid : {}".format(str(current_moodleBot.bot_id)))
                flask_logger.debug("moodleBot_list length : {}".format(str(len(moodleBot_list))))

                # 登入成功，新增 moodleBot 物件到 moodleBot_list
                moodleBot_list.append(current_moodleBot)
                return_data = jsonify({post_parameter.RESULT: post_parameter.RESULT_SUCCESS, post_parameter.USERID: str(current_moodleBot.bot_id)})
                flask_logger.debug("return_data : {}".format(return_data.json))
                return return_data
            else:
                userid_list.remove(userid_list[-1])
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
            userid = int(data[post_parameter.USERID])
            classification = data[post_parameter.CLASSIFICATION]
            sort = data[post_parameter.SORT]

            # 檢查 post data
            if classification not in ['past', 'inprogress']:
                raise server_exception.InvalidPostParameter("classification value error")
            elif sort not in ['fullname', 'ul.timeaccess desc']:
                return server_exception.InvalidPostParameter("sort value error")

            # 檢查 userid 是否存在
            if not check_userid_exist(userid):
                raise server_exception.UserIDNotExist(userid)
            
            # 取得 moodleBot 物件
            current_moodleBot = moodleBot_list[userid]

            # 取得課程資訊
            ret, course_list = current_moodleBot.get_enrolled_courses_by_timeline_classification(classification=classification, sort=sort)

            # 建立回傳的 json list
            return_data_list = []
            
            # 如果成功取得課程資訊
            if ret:
                # 插入一個 result = success 的 dict
                return_data_list.append({post_parameter.RESULT: post_parameter.RESULT_SUCCESS})
                return_data_list.append({post_parameter.COURSES: course_list})
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
            if not check_userid_exist(userid):
                raise server_exception.UserIDNotExist(userid)
            
            # 取得 moodleBot 物件
            current_moodleBot = moodleBot_list[userid]

            # 取得單個課程頁面
            current_moodleBot.get_course_page(courseid)
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
    # clear the terminal
    print(chr(27) + "[2J")
    app.run(debug=True)