# Simon Says
# 10/14/2018 - No CPX module
# Using only the 2 onboard buttons
# CPX conflict with loading audio, thus the borrowed Audio code for tones

import time
import array
import math
import neopixel
import board
import audioio
from random import randint
from digitalio import DigitalInOut, Direction, Pull


# Globals
pixels = neopixel.NeoPixel(board.NEOPIXEL, 10, brightness=.2)
pattern = []
sim_speed = 0.5
MAX_TIME = 10  # in seconds
MAX_ROUNDS = 8

# Colors
RED = (0x10, 0, 0)
YELLOW = (0x10, 0x10, 0)
GREEN = (0, 0x10, 0)
BLUE = (0, 0, 0x10)
BLACK = (0, 0, 0)

# Pixels/LEDs
PIXEL_LEFT = 2
PIXEL_RIGHT = 7
SIM = [
    { 
        'button': DigitalInOut(board.BUTTON_A),
        'light': PIXEL_LEFT,
        'color': GREEN,
        'tone': 360
    },
    {
        'button': DigitalInOut(board.BUTTON_B),
        'light': PIXEL_RIGHT,
        'color': YELLOW,
        'tone': 390
    }
]

    
def setup():
    # Setup all buttons as inputs
    for s in SIM:
        s["button"].direction = Direction.INPUT
        s["button"].pull = Pull.DOWN

    pixels.fill((0, 0, 0))
    pixels.show()


def make_pattern(level):
    choice = randint(0, (len(SIM) - 1))
    pattern.append(choice)


def show_pattern():
    for p in pattern:
        start_tone(SIM[p]['tone'])
        pixels[SIM[p]['light']] = SIM[p]['color']
        pixels.show()
        time.sleep(sim_speed * 2)
        stop_tone()
        pixels[SIM[p]['light']] = BLACK
        pixels.show()
        time.sleep(sim_speed)


def user_input_loop():
    start_time = time.monotonic()
    last_press = None
    pattern_place = 0
    
    while time.monotonic() < (start_time + MAX_TIME):
        x = check_button_press()
        if x != last_press:
            
            # If the button was released, turn out lights
            if x is None:
                pixels.fill((0, 0, 0))
                pixels.show()
                last_press = None
                stop_tone()
                
                # Check for win state
                if pattern_place == len(pattern):
                    time.sleep(.6)
                    return True
                continue

            # This should be a new button press
            # light up the color next to button
            pixels.fill((0, 0, 0))
            pixels[SIM[x]['light']] = SIM[x]['color']
            pixels.show()
            start_tone(SIM[x]['tone'])
            
            # check if it was the right button
            if pattern[pattern_place] == x:
                # Good choice
                print("Good choice")
                pattern_place += 1
            else:
                time.sleep(.2)
                stop_tone()
                wrong_choice(pattern[pattern_place], x)
                return False
    
        last_press = x
    print("Time Out")
    wrong_choice(pattern[pattern_place], 0)
    return False

    
def check_button_press():
    for i in range(len(SIM)):
        if SIM[i]["button"].value:
            return i
    return None


def wrong_choice(correct, incorrect):
    print("Wrong choice")
    start_tone(300)
    # Blink the right choice a few times
    for i in range(5):
        pixels.fill((0, 0x10, 0x10))
        pixels[SIM[correct]['light']] = SIM[correct]['color']
        pixels.show()
        time.sleep(.25)
        pixels.fill((0, 0, 0))
        pixels.show()       
        time.sleep(.25)
    stop_tone()

        
def main():
    global sim_speed, pattern
    
    while True:
        for i in range(MAX_ROUNDS):
            make_pattern(i)
            show_pattern()
            good_round = user_input_loop()
            
            # Check for incorrect answer
            if not good_round:
                break
            
            # Speed up each time we add a new pattern
            sim_speed = sim_speed - 0.05
            time.sleep(1.0)

        print("Starting new round")    
        pattern = []
        sim_speed = 0.5
        time.sleep(3)


# Audio Code
_sample = None
def setup_audio():
    _speaker_enable = DigitalInOut(board.SPEAKER_ENABLE)
    _speaker_enable.switch_to_output(value=False)
    _speaker_enable.value = True
    
def _sine_sample(length):
    tone_volume = (2 ** 15) - 1
    shift = 2 ** 15
    for i in range(length):
        yield int(tone_volume * math.sin(2*math.pi*(i / length)) + shift)
   
def start_tone(frequency):
    global _sample

    length = 100
    if length * frequency > 350000:
        length = 350000 // frequency
    _sine_wave = array.array("H", _sine_sample(length))
    _sample = audioio.AudioOut(board.SPEAKER)
    _sine_wave_sample = audioio.RawSample(_sine_wave)
    
    _sine_wave_sample.sample_rate = int(len(_sine_wave) * frequency)
    if not _sample.playing:
        _sample.play(_sine_wave_sample, loop=True)
        
def stop_tone():
    global _sample
    if _sample is not None and _sample.playing:
        _sample.stop()
        _sample.deinit()
        _sample = None


# Start main code
setup()
setup_audio()
main()