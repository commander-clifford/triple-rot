import board
from adafruit_seesaw import seesaw, rotaryio, digitalio

i2c = board.I2C()
seesaws = [seesaw.Seesaw(i2c, addr) for addr in (0x36, 0x37, 0x3a)]

for i, ss in enumerate(seesaws):
    ss_product = (ss.get_version() >> 16) & 0xFFFF
    print("Found product {} for seesaw {}".format(ss_product, i))
    if ss_product != 4991:
        print("Wrong firmware loaded? Expected 4991")

buttons = [digitalio.DigitalIO(ss, 24) for ss in seesaws]
button_held = [False] * len(seesaws)

encoders = [rotaryio.IncrementalEncoder(ss) for ss in seesaws]
last_positions = [None] * len(seesaws)

while True:
    for i, encoder in enumerate(encoders):
        position = -encoder.position
        if position != last_positions[i]:
            last_positions[i] = position
            print("Position for seesaw {}: {}".format(i, position))
        button = buttons[i]
        if not button.value and not button_held[i]:
            button_held[i] = True
            print("Button {} pressed".format(i))
        if button.value and button_held[i]:
            button_held[i] = False
            print("Button {} released".format(i))
