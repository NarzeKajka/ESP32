from random import randint

import machine
import time

from umqtt.simple import MQTTClient
import wifi_setup
import network
import time


# Setup WiFi

# TODO: odbieranie tokena z aplikacji

def connect_to_wifi(wifi, essid, password, timeout):
    global ssid, pwd
    if not wifi.isconnected():
        print("Connecting to WiFi network...")
        wifi.connect(essid, password)
        # Wait until connected
        t = time.ticks_ms()
        while not wifi.isconnected():
            if time.ticks_diff(time.ticks_ms(), t) > timeout:
                wifi.disconnect()
                print("Timeout. Could not connect.")
                ssid, pwd = wifi_setup.ap_mode()
                return connect_to_wifi(wifi, ssid, pwd, timeout)
                # return False
        print("Successfully connected to " + essid)
        return True
    else:
        print("Already connected")
        return True


ssid, pwd, token = wifi_setup.ap_mode()

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
# wlan.connect(ssid, pwd)

connect_to_wifi(wlan, ssid, pwd, 10000)

while not wlan.isconnected():
    pass
print(wlan.ifconfig())
print("Połączono z WiFi")

# Dane Azure IoT Central
MQTT_SERVER = 'IOTprojekt.azure-devices.net'
SCOPE_ID = ''
DEVICE_ID = 'device1'
PRIMARY_KEY = 'SharedAccessSignature sr=IOTprojekt.azure-devices.net%2Fdevices%2Fdevice1&sig=fcIQpH8Vo6eRSFH5sO80tUjFcojToevYxlJtKuEQAWs%3D&se=1708636469'
USERNAME = '{}/{}/api-version=2018-06-30'.format(MQTT_SERVER, DEVICE_ID)

# Konfiguracja MQTT
MQTT_CLIENT = MQTTClient(client_id=DEVICE_ID, server=MQTT_SERVER, user=USERNAME, password=PRIMARY_KEY,
                         ssl=True)

MQTT_CLIENT.connect()


# Inicjalizacja I2C dla TMP102
# i2c = machine.I2C(scl=machine.Pin(22), sda=machine.Pin(21))
# TMP102_ADDR = 0x48


# Funkcja do wysyłania danych do Azure IoT Central
def send_data(temperature):
    MQTT_CLIENT.connect()
    message = b'{"temperature":' + str(temperature) + b'}'
    MQTT_CLIENT.publish("devices/" + DEVICE_ID + "/messages/events/", message)
    MQTT_CLIENT.disconnect()


# Główna pętla
while True:
    # Odczyt danych z czujnika
    # data = i2c.readfrom_mem(TMP102_ADDR, 0x00, 2)
    # temp = (data[0] << 4) | (data[1] >> 4)
    temp = 1000

    # Konwersja do temperatury
    temperature = temp * 0.0625

    print("Temperatura:", temperature, "°C")
    send_data(temperature)
    time.sleep(5)
