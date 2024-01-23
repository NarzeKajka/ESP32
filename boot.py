# boot.py -- run on boot-up
import gc
import wifi_setup
import network
import time

gc.collect()


def connectToWifi(wifi, essid, password, timeout):
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
                return connectToWifi(wifi, ssid, pwd, timeout)
                # return False
        print("Successfully connected to " + essid)
        return True
    else:
        print("Already connected")
        return True


ssid, pwd = wifi_setup.ap_mode()

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
# wlan.connect(ssid, pwd)

connectToWifi(wlan, ssid, pwd, 10000)

while not wlan.isconnected():
    pass
print(wlan.ifconfig())
print("Połączono z WiFi")
