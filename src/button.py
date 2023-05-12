import utime
from machine import Pin

def noop_button_handler(pin):
  pass

# button is waiting for a press
BUTTON_STATE_IDLE    = 0
# the button has been freshly pressed and needs a timeout set
BUTTON_STATE_PRESSED = 1
# the button is waiting to be cancelled before sending
BUTTON_STATE_WAITING = 2
# button is ready to send an event
BUTTON_STATE_SEND    = 3

# time to debounce a button press in milliseconds
DEBOUNCE_DELAY = 50
# the amount of time to give for cancelling an initiated event in milliseconds
WAIT_DELAY = 5000

class Button:
    def __init__(self, pin_id, button_id, irq_handler=noop_button_handler):
        self.pin = Pin(pin_id, Pin.IN, Pin.PULL_UP)
        self.pin.irq(handler=irq_handler, trigger=Pin.IRQ_RISING)
        self.button_id = button_id
        self.debounce_time = 0
        self.wait_time = 0
        self.state = BUTTON_STATE_IDLE

        print(f'Button {button_id} created on pin {pin_id}')

    def handle_interrupt(self, pin):
        if pin is self.pin and utime.ticks_ms() > self.debounce_time:
            self.debounce_time = utime.ticks_ms() + 200
            self.state = BUTTON_STATE_PRESSED if self.state == BUTTON_STATE_IDLE else BUTTON_STATE_IDLE
            return True
        return False

    def handle_tick(self, ticks):
        # doing nothing, keep the house clean
        if self.state == BUTTON_STATE_IDLE:
            self.debounce_time = 0
            self.wait_time = 0
        # button was pressed since the last loop, start the countdown
        elif self.state == BUTTON_STATE_PRESSED:
            self.wait_time = ticks + WAIT_DELAY
            self.state = BUTTON_STATE_WAITING
        # we're waiting for the user to cancel before sending the event
        elif self.state == BUTTON_STATE_WAITING:
            self.state = BUTTON_STATE_SEND if ticks > self.wait_time else BUTTON_STATE_WAITING

    def should_send_event(self):
        if self.state == BUTTON_STATE_SEND:
            self.state = BUTTON_STATE_IDLE
            return True
        return False
