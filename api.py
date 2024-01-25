import urequests

API_URL = "https://a2.listamc.pl/api/v1/"


def register_device(token: str):
    # Register device
    print("Registering device...")
    response = urequests.post(API_URL + "users/devices", headers={
        'Authorization': 'Bearer ' + token
    })
    print(response.content)
    print(response.json())
    print("Device registered")
    # TODO: return device id, credentials
    d = response.json()
    return d['id'], d['name'], d['sas_token']
