import network
import time
import urequests
import utime
from machine import Pin

# TODO figure out how to move this to some imported config...
NETWORK_SSID="__SSID__"
NETWORK_PASS="__PASS__"

led_pin = Pin("LED", Pin.OUT)

# the pins to which the buttons are connected and the order
# in which they should be assigned to the outgoing press
button_pins = [6, 7, 8, 9, 10, 11, 12, 13]
button_pin_map = {}

def connect_wlan():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(NETWORK_SSID, NETWORK_PASS)

    connect_wait_seconds = 10
    led_pin.toggle()
    while connect_wait_seconds > 0:
        status = wlan.status()
        if status < 0 or status >= 3:
            break
        connect_wait_seconds -= 1
        led_pin.toggle()
        time.sleep(1)

    if wlan.status() != 3:
        raise RuntimeError('Unable to connect to wireless network')
    else:
        ip_address = wlan.ifconfig()
        print(f'Connected to network with IP: {ip_address[0]}')
        led_pin.value(1)

def send_button_press_event(button_id):
    # TODO: send to LifeLog endpoint when that's up and running
    response = urequests.post(
        'https://wx.hakkslab.io/observation',
        headers={
            'Content-Type': 'text/json',
        },
        data='{"stationKey":"LBTN", "stationName": "LifeButton", "observationType": "temperature", "observationValue": 42}'
    )
    print('Send press event')
    response.close()

def handle_button_press(pin):
    pin.irq(handler=None)

    # loop through the buttons to find the one that raised the interrupt
    for key in button_pin_map:
        value = button_pin_map[key]
        index, button = value
        if pin is button:
            print(f'Sending event for button #{index}')
            send_button_press_event(index)
            time.sleep(1)
            break

    pin.irq(handler=handle_button_press, trigger=Pin.IRQ_FALLING)


def init_buttons():
    i = 0
    for pin_id in button_pins:
        button = Pin(pin_id, Pin.IN, Pin.PULL_DOWN)
        button.irq(handler=handle_button_press, trigger=Pin.IRQ_FALLING)
        # save this as a tuple of the button assignment and the pin object
        button_pin_map[pin_id] = (i, button)
        print(f'Assigned pin {pin_id} to button #{i}')
        i += 1

def main():
    init_buttons()
    connect_wlan()
    while True:
        pass

main()
