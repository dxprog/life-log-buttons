import network
import time
import urequests
import utime
from machine import Pin

from config import NETWORK_PASS, NETWORK_SSID
from button import Button

led_pin = Pin("LED", Pin.OUT)

# the pins to which the buttons are connected and the order
# in which they should be assigned to the outgoing press
button_pins = [6, 7, 8, 9, 10, 11, 12, 13]
buttons = []

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
    # response = urequests.post(
    #     'https://wx.hakkslab.io/observation',
    #     headers={
    #         'Content-Type': 'text/json',
    #     },
    #     data='{"stationKey":"LBTN", "stationName": "LifeButton", "observationType": "temperature", "observationValue": 42}'
    # )
    print(f'Send press event for button {button_id}')
    led_pin.toggle()
    utime.sleep_ms(200)
    led_pin.toggle()
    # response.close()

def handle_button_press(pin):
    # loop through the buttons to find the one that raised the interrupt
    for button in buttons:
        if button.handle_interrupt(pin):
            send_button_press_event(button.button_id)
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
        pass

main()
