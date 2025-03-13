import telebot
import requests
import random
import string
from datetime import datetime, timedelta
import sqlite3

# Define MIN_COINS_REQUIRED
MIN_COINS_REQUIRED = 5000

id = requests.get('https://api.ipify.org').text
TOKEN = '6337073929:AAGsvCXWRJ6Ol-K5V1ZCJ6vmcLll-0UsnE8'
bot = telebot.TeleBot(TOKEN)

# Add the admin's ID
ADMIN_ID = 5805939083

def create_connection():
    return sqlite3.connect('1.db')

def create_tables():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS links (
            user_id INTEGER,
            link TEXT,
            key TEXT,
            expire_at TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            coin INTEGER,
            username TEXT
        )
    ''')
    conn.commit()
    conn.close()

def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def create_all_tables():
    create_tables()

@bot.message_handler(commands=['congcoin'])
def congcoin_command(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, 'You do not have the permission to use this command.')
        return

    if len(message.text.split()) != 3:
        bot.send_message(message.chat.id, 'Syntax: /congcoin +id +coin_amount')
        return

    _, user_id_to_add, coins_to_add = message.text.split()
    user_id_to_add = int(user_id_to_add)
    coins_to_add = int(coins_to_add)

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT coin FROM users WHERE user_id = ?', (user_id_to_add,))
    result = cursor.fetchone()

    if result:
        current_coins = result[0]
        new_coins = current_coins + coins_to_add
        cursor.execute('UPDATE users SET coin = ? WHERE user_id = ?', (new_coins, user_id_to_add))
        conn.commit()
        bot.send_message(message.chat.id, f'Added {coins_to_add} coins to the user with ID {user_id_to_add}.')
    else:
        bot.send_message(message.chat.id, f'User with ID {user_id_to_add} does not exist.')

    conn.close()

@bot.message_handler(commands=['mua'])
def mua_command(message):
    create_all_tables()

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT coin FROM users WHERE user_id = ?', (message.from_user.id,))
    result = cursor.fetchone()

    if result:
        current_coins = result[0]
        if current_coins >= MIN_COINS_REQUIRED:
            new_coins = current_coins - MIN_COINS_REQUIRED
            cursor.execute('UPDATE users SET coin = ? WHERE user_id = ?', (new_coins, message.from_user.id))
            conn.commit()

            try:
                random_admin = generate_random_string(10)
                expire_date = datetime.now() + timedelta(hours=24)
                expire_at = expire_date.strftime('%Y-%m-%d')
                key = f'{random_admin}'

                link_api = f'http://{id}:2024/api?key={key}&host=[host]&port=[port]&time=[time]&methods=[methods]'
                original_link = f'http://127.0.0.1:8080/api?key={random_admin}&hsd=14h'
                user_id = message.from_user.id

                # Make the HTTP request to the API
                response = requests.get(original_link)
                response.raise_for_status()  # Check for HTTP errors

                bot.send_message(message.chat.id,
                                 f'- Your original api c2-ddos:\n {link_api}\n- Plan api ddos của bạn:\n- key: {random_admin},\n- HSD: 24H,\n- Methods: BYPASS, 404')
            except requests.exceptions.RequestException as e:
                bot.send_message(message.chat.id, f'Failed to generate api URL. Error: {str(e)}')
        else:
            bot.send_message(message.chat.id, 'Not enough coins (5000 coins required) to purchase the api c2.')
    else:
        bot.send_message(message.chat.id, 'User does not exist.')

    conn.close()

@bot.message_handler(commands=['coin'])
def coin_command(message):
    user_id = message.from_user.id
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT coin FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()

    if result:
        current_coins = result[0]
        bot.send_message(message.chat.id, f'Your remaining coins: {current_coins}')
    else:
        bot.send_message(message.chat.id, 'User does not exist.')

@bot.message_handler(commands=['chuyencoin'])
def chuyencoin_command(message):
    if len(message.text.split()) != 3:
        bot.send_message(message.chat.id, 'Syntax: /chuyencoin +id +coin_amount')
        return

    _, user_id_to_transfer, coins_to_transfer = message.text.split()
    user_id_to_transfer = int(user_id_to_transfer)
    coins_to_transfer = int(coins_to_transfer)

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT coin FROM users WHERE user_id = ?', (message.from_user.id,))
    sender_result = cursor.fetchone()

    if sender_result:
        sender_coins = sender_result[0]
        if sender_coins >= coins_to_transfer >= 0:
            new_sender_coins = sender_coins - coins_to_transfer
            cursor.execute('UPDATE users SET coin = ? WHERE user_id = ?', (new_sender_coins, message.from_user.id))

            cursor.execute('SELECT coin FROM users WHERE user_id = ?', (user_id_to_transfer,))
            receiver_result = cursor.fetchone()

            if receiver_result:
                receiver_coins = receiver_result[0]
                new_receiver_coins = receiver_coins + coins_to_transfer
                cursor.execute('UPDATE users SET coin = ? WHERE user_id = ?', (new_receiver_coins, user_id_to_transfer))
                conn.commit()

                bot.send_message(message.chat.id, f'Transferred {coins_to_transfer} coins to the user with ID {user_id_to_transfer}.')
            else:
                bot.send_message(message.chat.id, f'Receiver with ID {user_id_to_transfer} does not exist.')
        else:
            bot.send_message(message.chat.id, 'Invalid coin amount or insufficient coins to transfer.')
    else:
        bot.send_message(message.chat.id, 'Sender does not exist.')

    conn.close()

@bot.message_handler(commands=['id'])
def id_command(message):
    user_id = message.from_user.id
    bot.send_message(message.chat.id, f'Your ID is: {user_id}')

@bot.message_handler(commands=['start'])
def start_command(message):
    create_all_tables()
    bot.send_message(message.chat.id, 'Welcome to our bot!\n'
                                      'Use the following commands to perform various functions:\n'
                                      '/mua - Purchase a api ddos c2\n'
                                      '/id - Get your ID\n'
                                      '/chuyencoin +id +coin_amount - Transfer your coins to another user\n'
                                      '/coin - Check your coin balance\n'
                                      '\n@$- For coin exchange, contact @citylightverry, exchange rate: 1k vnd = 1k coin\n'
                                      '\n@$- Thank you for your trust and using our bot!')

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO users (user_id, coin) VALUES (?, ?)', (message.from_user.id, 0))
    conn.commit()

    if message.from_user.username:
        cursor.execute('UPDATE users SET username = ? WHERE user_id = ?', (message.from_user.username, message.from_user.id))
        conn.commit()

    conn.close()

if __name__ == "__main__":
    bot.remove_webhook()  
    bot.polling()
