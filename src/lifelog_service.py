import network
import urequests
import ujson
import ubinascii

class LifelogService:
  def __init__(self, ssid, password, api_path):
    self.wlan = network.WLAN(network.STA_IF)

    self.ssid = ssid
    self.password = password
    self.api_path = api_path

    self.ip_address = None
    self.device_id = None
    self.is_registered = False
    pass

  def connect(self):
    """
    Begins the process of connecting to the configured WiFi access point
    """
    self.wlan.active(True)
    self.wlan.connect(self.ssid, self.password)

  def is_connected(self):
    """
    Checks to see if the device is connected to the access point. If it is,
    registers the device with the Lifelog service and returns true. Throws
    if there was an error connected.
    """
    status = self.wlan.status()

    if status == network.STAT_GOT_IP:
      self.ip_address = self.wlan.ifconfig()
      self.device_id = ubinascii.hexlify(self.wlan.config('mac')).decode()
      print(f'Connected to network with IP: {self.ip_address[0]}')
      print(f'Device ID: {self.device_id}')

      self.register()

      return True

    elif (
      status == network.STAT_WRONG_PASSWORD or
      status == network.STAT_NO_AP_FOUND or
      status == network.STAT_CONNECT_FAIL
    ):
      raise Exception('Error connecting to the access point', status)

  def register(self):
    """
    Registers the device with the Lifelog service
    """
    if self.is_registered:
      return

    print('Registering device with service...')
    response = urequests.post(
        f'{self.api_path}/device',
        headers={
            'Content-Type': 'application/json',
        },
        data=ujson.dumps({
            'deviceId': self.device_id,
        })
    )
    response.close()
    self.is_registered = True
    print('Done!')

  def send_event(self, button_id):
    # TODO: send to LifeLog endpoint when that's up and running
    print(f'Send press event for button {button_id}')
    response = urequests.post(
      f'{self.api_path}/event',
      headers={
        'Content-Type': 'application/json',
      },
      data=ujson.dumps({
        'deviceId': self.device_id,
        'buttonIndex': button_id,
      })
    )
    response.close()
