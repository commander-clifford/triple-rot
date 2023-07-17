# SPDX-FileCopyrightText: 2021 John Furcean
# SPDX-License-Identifier: MIT

"""I2C rotary encoder simple test example."""

import board
import time
from adafruit_seesaw import seesaw, rotaryio, digitalio
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
import usb_hid

ENCODER_ADDRESSES = [0x36, 0x37, 0x3A]

i2c = board.I2C()  # uses board.SCL and board.SDA

# setup HID devices
kbd = Keyboard(usb_hid.devices)

# create a list of seesaw objects for each encoder
seesaw_encoders = [seesaw.Seesaw(i2c, addr=address) for address in ENCODER_ADDRESSES]

# Define button and encoder actions for each encoder
encoder_actions = [
    {
        "button": Keycode.ENTER,
        "cw": [Keycode.TAB],  # Clockwise
        "ccw": [Keycode.SHIFT, Keycode.TAB],  # Counter-clockwise
    },
    {
        "button": Keycode.SPACEBAR,
        "cw": [Keycode.RIGHT_ARROW],
        "ccw": [Keycode.LEFT_ARROW],
    },
    {
        "button": Keycode.ESCAPE,
        "cw": [Keycode.DOWN_ARROW],
        "ccw": [Keycode.UP_ARROW],
    },
]

for idx, ss in enumerate(seesaw_encoders):
    seesaw_product = (ss.get_version() >> 16) & 0xFFFF
    print(f"Found product {seesaw_product} at address {ENCODER_ADDRESSES[idx]}")
    if seesaw_product != 4991:
        print("Wrong firmware loaded?  Expected 4991")

    ss.pin_mode(24, ss.INPUT_PULLUP)  # Using INPUT_PULLUP mode

# create lists for buttons and encoders for each seesaw object
button_held = [False for _ in seesaw_encoders]
encoders = [rotaryio.IncrementalEncoder(ss) for ss in seesaw_encoders]
last_positions = [-encoder.position for encoder in encoders]  # Initialize positions with current position

def handle_button(ss, idx):
    global button_held
    button_value = ss.digital_read(24)
    if not button_value and not button_held[idx]:
        time.sleep(0.05)  # Debouncing delay
        if not ss.digital_read(24):  # Check button state again after delay
            button_held[idx] = True
            print(f"Button pressed on encoder {ENCODER_ADDRESSES[idx]}")
            kbd.send(encoder_actions[idx]["button"])  # Send button action
    elif button_value and button_held[idx]:
        button_held[idx] = False
        print(f"Button released on encoder {ENCODER_ADDRESSES[idx]}")

def handle_encoder(encoder, idx):
    global last_positions
    position = -encoder.position
    if position != last_positions[idx]:
        print(f"Encoder {ENCODER_ADDRESSES[idx]} position: {position}")
        if position > last_positions[idx]:
            kbd.send(*encoder_actions[idx]["cw"])  # Send clockwise action
        else:
            kbd.send(*encoder_actions[idx]["ccw"])  # Send counter-clockwise action
        last_positions[idx] = position

while True:
    for idx in range(len(encoders)):
        handle_button(seesaw_encoders[idx], idx)
        handle_encoder(encoders[idx], idx)
