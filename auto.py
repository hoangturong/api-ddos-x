import subprocess
import threading

def run_command(command):
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error while executing '{command}': {e}")

def run_in_thread(file_name):
    command = f"python {file_name}"
    run_command(command)

def main():
    api = "api.py"
    bot = "bot.py"
    user = "user.py"
    proxy = "proxy.py"

    # Tạo danh sách các luồng
    threads = []

    # Thêm mỗi tệp vào danh sách luồng
    threads.append(threading.Thread(target=run_in_thread, args=(api,)))
    threads.append(threading.Thread(target=run_in_thread, args=(bot,)))
    threads.append(threading.Thread(target=run_in_thread, args=(user,)))
    threads.append(threading.Thread(target=run_in_thread, args=(proxy,)))

    # Bắt đầu chạy tất cả các luồng
    for thread in threads:
        thread.start()

    # Chờ tất cả các luồng hoàn thành
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()
