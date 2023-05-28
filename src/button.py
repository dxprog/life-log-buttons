import utime
from machine import Pin, PWM

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
DEBOUNCE_DELAY = 250
# the amount of time to give for cancelling an initiated event in milliseconds
WAIT_DELAY = 5000
# frequency to use for LED fadeout
PWM_FREQ = 5000
MAX_DUTY_CYCLE = 65535

class Button:
    def __init__(self, button_pin=None, led_pin=None, button_id=None, irq_handler=noop_button_handler):
        if (
           button_pin is None or
           led_pin is None or
           button_id is None
        ):
            raise Exception('Button must have a switch pin, led pin, and button ID')

        # LED init
        self.led_pin = PWM(Pin(led_pin))
        self.led_pin.freq(PWM_FREQ)
        self.led_pin.duty_u16(0)

        # button init
        self.button_pin = Pin(button_pin, Pin.IN, Pin.PULL_UP)
        self.button_pin.irq(handler=irq_handler, trigger=Pin.IRQ_RISING)
        self.button_id = button_id

        # counters and state
        self.debounce_time = 0
        self.wait_time = 0
        self.state = BUTTON_STATE_IDLE

        print(f'Button {button_id} created on pin {button_pin} and led {led_pin}')

    def handle_interrupt(self, pin):
        if pin is self.button_pin and utime.ticks_ms() > self.debounce_time:
            self.debounce_time = utime.ticks_ms() + DEBOUNCE_DELAY
            self.state = BUTTON_STATE_PRESSED if self.state == BUTTON_STATE_IDLE else BUTTON_STATE_IDLE
            self.led_pin.duty_u16(0 if self.state == BUTTON_STATE_IDLE else MAX_DUTY_CYCLE)
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
            if ticks > self.wait_time:
                self.state = BUTTON_STATE_SEND
                led_fade = 0
            else:
                led_fade = ((self.wait_time - ticks) / WAIT_DELAY) * MAX_DUTY_CYCLE

            self.led_pin.duty_u16(int(led_fade))

    def should_send_event(self):
        if self.state == BUTTON_STATE_SEND:
            self.state = BUTTON_STATE_IDLE
            self.led_pin.duty_u16(0)
            return True
        return False
