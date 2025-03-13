import re
import requests
import threading
import time

# Định nghĩa hàm start để lấy proxy từ URL cụ thể
def start(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            # Trích xuất các proxy sử dụng biểu thức chính quy đơn giản
            proxies = re.findall(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}:[0-9]+\b', response.text)
            
            # Lưu các proxy vào tệp 'proxy.txt'
            with open('proxy.txt', 'a') as file:
                for proxy in proxies:
                    file.write(proxy + '\n')
                
        else:
            print(f"Lấy proxy từ {url} thất bại. Mã trạng thái: {response.status_code}")
    except Exception as e:
        print(f"Lỗi khi lấy proxy từ {url}: {str(e)}")

# Hàm để thực hiện vòng lặp lấy proxy mỗi 2 phút
def fetch_proxies_periodically():
    while True:
        # Gọi lại hàm start cho mỗi URL
        for url in urls.splitlines():
            if url:
                start(url)

        # Đợi 2 phút trước khi lấy proxy tiếp theo
        time.sleep(120)

# Danh sách các URL chứa danh sách proxy
urls = '''
https://api.openproxylist.xyz/all.txt
https://api.proxyscrape.com/?request=displayproxies&proxytype=all
https://api.proxyscrape.com/v2/?request=displayproxies&protocol=all
'''

# Xóa nội dung của tệp 'proxy.txt' nếu có hoặc tạo một tệp mới
with open('proxy.txt', 'w'):
    pass

# Tạo một luồng cho vòng lặp lấy proxy mỗi 2 phút
fetch_thread = threading.Thread(target=fetch_proxies_periodically)

# Bắt đầu luồng vòng lặp
fetch_thread.start()

# Chờ cho luồng vòng lặp kết thúc
fetch_thread.join()
