from flask import Flask, request, jsonify
import datetime
import uuid

app = Flask(__name__)
user_data_file = 'user.txt'

def generate_random_key():
    return str(uuid.uuid4())

def get_expiration_date():
    return (datetime.datetime.now() + datetime.timedelta(hours=24)).strftime('%Y-%m-%d')

@app.route('/api', methods=['GET'])
def process_request():
    # Lấy thông tin từ tham số trong URL
    random_admin = request.args.get('key', '')
    expiration_date = request.args.get('hsd', '24h')
    
    # Tạo key theo định dạng y-m-d
    current_date = datetime.datetime.now().strftime('%Y-%m-%d')
    
    # Ghi thông tin vào file user.txt
    with open(user_data_file, 'a') as file:
        file.write(f'{random_admin}:{current_date}\n')
    
    # Trả về dữ liệu dưới dạng JSON
    response_data = {
        'message': f'with key: {random_admin}',
        'success': True
    }
    
    return jsonify(response_data)

if __name__ == '__main__':
    app.run(port=8080)
