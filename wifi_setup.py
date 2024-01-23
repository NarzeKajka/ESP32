import json
import os
import cryptolib
import gc
import uos

import network
import socket
from binascii import a2b_base64

STORE_FILE = 'wificonf.json'
SETUP_SSID = 'sensor'

key = b'[verysecretaeskey256aaaaaaaaaaa]'
iv = b'secret-iv-123456'

# nie zmieniać:
NEW_SSID = ''
NEW_PASS = ''
NEW_TOKEN = ''

# tryb CBC


#     TODO: zapisywanie zakończenia konfiguracji (true do pliku)

try:
    with open(STORE_FILE, 'r') as f:
        content = json.load(f)
        print(content, len(content))

        if content['configured']:
            print('configured')
        else:
            print('not configured')
except OSError as e:
    with open(STORE_FILE, 'w') as f:
        json.dump({'configured': False, 'ssid': '', 'password': ''}, f)

def response_ok(conn):
    response_body = json.dumps({'message': 'POST request received'})
    response_headers = 'HTTP/1.1 200 OK\r\n'
    response_headers += 'Content-Type: application/json\r\n'
    response_headers += 'Content-Length: {}\r\n\r\n'.format(len(response_body))
    conn.sendall(response_headers.encode('utf-8'))
    conn.sendall(response_body.encode('utf-8'))


def handle_request(conn, _conf):
    global NEW_SSID, NEW_PASS, NEW_TOKEN
    gc.collect()
    request = conn.recv(1024)
    request_str = request.decode('utf-8')

    headers, body = request_str.split('\r\n\r\n', 1)

    if headers.startswith('POST'):
        try:
            print('Encrypted:', body)
            unb64_ciphertext = a2b_base64(body.strip().encode())

            crypto = cryptolib.aes(key, 2, iv)
            decrypted = crypto.decrypt(unb64_ciphertext)

            pad = decrypted[-1]
            decrypted_data = decrypted[:-pad]

            print('Decrypted:', decrypted_data)

            # convert to json
            json_body = json.loads(decrypted_data)
            print('JSON Body:', json_body)
            _conf = False
            NEW_SSID = json_body['ssid']
            NEW_PASS = json_body['password']
            NEW_TOKEN = json_body['token']

            response_ok(conn)

            return True
        except ValueError as e:
            print('Invalid data', e)
            print('Invalid data')
            response_ok(conn)

            return False


    else:
        conn.sendall('HTTP/1.1 400 Bad Request\r\n\r\n'.encode('utf-8'))

    conn.close()


def ap_mode():
    global NEW_SSID, NEW_PASS
    _conf = False

    with open(STORE_FILE, 'r') as f:
        # content = f.read().strip()
        content = json.load(f)
        print(content, len(content))

        if content['configured']:
            print('configured')
            print(content['ssid'], content['password'])
            NEW_SSID = content['ssid']
            NEW_PASS = content['password']
        else:
            print('not configured')
            _conf = True

    if _conf:
        ap = network.WLAN(network.AP_IF)
        ap.active(True)
        ap.config(essid=SETUP_SSID)

        print('SSID:', ap.config('essid'))

        while ap.active() == False:
            pass

        print('AP active')

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', 80))
        s.listen(5)

        while _conf:
            conn, addr = s.accept()
            print('Got a connection from %s' % str(addr))
            _conf = not handle_request(conn, _conf)
            print(_conf)

        # close socket and AP
        s.close()
        ap.active(False)

    print('SSID:', NEW_SSID)
    print('PASS:', NEW_PASS)
    print('TOKEN:', NEW_TOKEN)

    return NEW_SSID, NEW_PASS, NEW_TOKEN
