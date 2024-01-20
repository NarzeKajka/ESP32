import machine
import network
import time
from umqtt.simple import MQTTClient

# Dane WiFi
SSID = ''
PASSWORD = ''

# Dane Azure IoT Central
SCOPE_ID = ''
DEVICE_ID = ''
PRIMARY_KEY = ''

# Konfiguracja MQTT
MQTT_CLIENT = MQTTClient(client_id=DEVICE_ID, server=MQTT_SERVER, user=DEVICE_ID + "@" + SCOPE_ID, password=PRIMARY_KEY, ssl=True)

# Inicjalizacja I2C dla TMP102
i2c = machine.I2C(scl=machine.Pin(22), sda=machine.Pin(21))
TMP102_ADDR = 0x48

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)
while not wlan.isconnected():
    pass
print("Połączono z WiFi")

# Funkcja do wysyłania danych do Azure IoT Central
def send_data(temperature):
    MQTT_CLIENT.connect()
    message = b'{"temperature":' + str(temperature) + b'}'
    MQTT_CLIENT.publish("devices/" + DEVICE_ID + "/messages/events/", message)
    MQTT_CLIENT.disconnect()

# Główna pętla
while True:
    # Odczyt danych z czujnika
    data = i2c.readfrom_mem(TMP102_ADDR, 0x00, 2)
    temp = (data[0] << 4) | (data[1] >> 4)
    
    # Konwersja do temperatury
    temperature = temp * 0.0625
    
    print("Temperatura:", temperature, "°C")
    send_data(temperature)
    time.sleep(2)  
