import utime
from machine import Pin

def noop_button_handler(pin):
  pass

class Button:
    def __init__(self, pin_id, button_id, irq_handler=noop_button_handler):
        self.pin = Pin(pin_id, Pin.IN, Pin.PULL_UP)
        self.pin.irq(handler=irq_handler, trigger=Pin.IRQ_RISING)
        self.button_id = button_id
        self.debounce_time = 0

        print(f'Button {button_id} created on pin {pin_id}')

    def handle_interrupt(self, pin):
        if pin is self.pin and utime.ticks_ms() > self.debounce_time:
            self.debounce_time = utime.ticks_ms() + 2000
            return True
        return False
