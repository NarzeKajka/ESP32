import urequests

API_URL = "https://iot-api-v2.azurewebsites.net/api/v1/"

def register_device():
    # Register device
    print("Registering device...")
    response = urequests.post(API_URL + "users/devices", json={
        "name": "My device"
    })
    print(response.json())
    print("Device registered")
    # TODO: return device id, credentials
    return