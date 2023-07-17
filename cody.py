# SPDX-FileCopyrightText: 2021 John Furcean
# SPDX-License-Identifier: MIT

"""I2C rotary encoder simple test example."""

import board
import time
from adafruit_seesaw import seesaw, rotaryio, digitalio

ENCODER_ADDRESSES = [0x36, 0x37, 0x3A]

i2c = board.I2C()  # uses board.SCL and board.SDA

# create a list of seesaw objects for each encoder
seesaw_encoders = [seesaw.Seesaw(i2c, addr=address) for address in ENCODER_ADDRESSES]

for idx, ss in enumerate(seesaw_encoders):
    seesaw_product = (ss.get_version() >> 16) & 0xFFFF
    print(f"Found product {seesaw_product} at address {ENCODER_ADDRESSES[idx]}")
    if seesaw_product != 4991:
        print("Wrong firmware loaded?  Expected 4991")

    ss.pin_mode(24, ss.INPUT_PULLUP)  # Using INPUT_PULLUP mode

#time.sleep(0.2)  # Add a short delay before starting to read button states

# create lists for buttons and encoders for each seesaw object
button_held = [False for _ in seesaw_encoders]
encoders = [rotaryio.IncrementalEncoder(ss) for ss in seesaw_encoders]
last_positions = [None for _ in seesaw_encoders]

def handle_button(ss, idx):
    global button_held
    button_value = ss.digital_read(24)
    if not button_value and not button_held[idx]:
        time.sleep(0.05)  # Debouncing delay
        if not ss.digital_read(24):  # Check button state again after delay
            button_held[idx] = True
            print(f"Button pressed on encoder {ENCODER_ADDRESSES[idx]}")
    elif button_value and button_held[idx]:
        button_held[idx] = False
        print(f"Button released on encoder {ENCODER_ADDRESSES[idx]}")

def handle_encoder(encoder, idx):
    global last_positions
    position = -encoder.position
    if position != last_positions[idx]:
        last_positions[idx] = position
        print(f"Encoder {ENCODER_ADDRESSES[idx]} position: {position}")

while True:
    for idx in range(len(encoders)):
        handle_button(seesaw_encoders[idx], idx)
        handle_encoder(encoders[idx], idx)
