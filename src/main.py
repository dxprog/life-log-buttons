import network
import time
import utime
import urequests
import ujson
import ubinascii
from machine import Pin, PWM

from config import NETWORK_PASS, NETWORK_SSID
from button import Button

led_pin = Pin("LED", Pin.OUT)

device_id = None

# the pins to which the buttons are connected and the order
# in which they should be assigned to the outgoing press
button_pins = [6, 7, 8, 9, 10, 11, 12, 13]
buttons = []

def connect_wlan():
    global device_id

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
        device_id = ubinascii.hexlify(wlan.config('mac')).decode()
        print(f'Connected to network with IP: {ip_address[0]}')
        print(f'Device ID: {device_id}')
        register_device(device_id)
        led_pin.value(1)

def register_device(device_id):
    print('Registering device with service...')
    response = urequests.post(
        'https://api.babylog.net/device',
        headers={
            'Content-Type': 'application/json',
        },
        data=ujson.dumps({
            'deviceId': device_id,
        })
    )
    response.close()
    print('Done!')

def send_button_press_event(button_id):
    # TODO: send to LifeLog endpoint when that's up and running
    print(f'Send press event for button {button_id}')
    response = urequests.post(
        'https://api.babylog.net/event',
        headers={
            'Content-Type': 'application/json',
        },
        data=ujson.dumps({
            'deviceId': device_id,
            'buttonIndex': button_id,
        })
    )
    response.close()

def handle_button_press(pin):
    # loop through the buttons to find the one that raised the interrupt
    for button in buttons:
        if button.handle_interrupt(pin):
            print(f'Button press on {button.button_id}')
            break

def init_buttons():
    global button_pins

    i = 0
    for pin_id in button_pins:
        buttons.append(Button(pin_id, i, irq_handler=handle_button_press))
        i += 1

def main():
    connect_wlan()
    init_buttons()
    while True:
        for button in buttons:
            button.handle_tick(utime.ticks_ms())
            if button.should_send_event():
                send_button_press_event(button.button_id)

main()
