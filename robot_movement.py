### IMPORTS ###
import RPi.GPIO as GPIO
import time

### CONSTANTS ###
LOW = GPIO.LOW
HIGH = GPIO.HIGH

## percentage of power to give to each side
THROTTLE = {
    'L': 100,
    'R': 100,
}

## sides L or R; depth F: front wheels or B: back wheels; 
## index 1 = clockwise pin; index 2 = counter-clockwise pin
WHEEL_PINS = {
  "L": {
      "F": [13, 15],
      "B": [33, 31],
  },
  "R": {
      "F": [16, 18],
      "B": [40, 38],
    }
}

## pins used for power input
POWER_PINS = {
    "L": 32,
    "R": 35
}

## GPIO PWM objects
POWER = {}

### INITIALIZATION ###
def _initGPIO():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)

    for depths in WHEEL_PINS.values():
        for pinInputs in depths.values():
            for pin in pinInputs:
                GPIO.setup(pin, GPIO.OUT)
                print(pin)

    for side in ["L", "R"]:
        GPIO.setup(POWER_PINS[side], GPIO.OUT)
        POWER[side] = GPIO.PWM(POWER_PINS[side], 500)

def Cleanup():
    for side in ["L", "R"]:
        POWER[side].stop()
        ResetMovement(side)
    GPIO.cleanup()

_initGPIO()

### MOVEMENT FUNCTIONS ###

def ResetMovement(side): # 'L' or 'R'
    for pins in WHEEL_PINS[side].values():
        for pin in pins:
            GPIO.output(pin, LOW)
        
def MoveWheel(side, depth, dir, t, *_notIndependent): ## side = 'L': left, 'R': right | depth = 'F': front, 'B': back | dir = 1 or -1 | t = time in s
    if not _notIndependent:
        ResetMovement(side)
        POWER[side].start(THROTTLE[side])

    pinIndex = 0 if dir == 1 else 1 ## pin 2 is counter-clockwise throttle

    wheels = WHEEL_PINS[side][depth]
    GPIO.output(wheels[pinIndex], HIGH)
    GPIO.output(wheels[1 if pinIndex == 0 else 0], LOW)

    if not _notIndependent:
        time.sleep(t)
        POWER[side].stop()

## sides define included sides for movement, table w/ 'L' or 'R'; EX) ['L', 'R'] moves both sides
## same with depths; EX) ['F', 'B'] moves both depths | dir = 1 or -1 | t = time in s
## EX) Move(['L', 'R'], ['F', 'B'], 1, 2) -- moves all wheels in clockwise direction for 2s
def Move(sides, depths, dir, t):
    for side in ["L", "R"]: ## stops all movement
        ResetMovement(side)

    for side in sides:
        POWER[side].start(THROTTLE[side])
        for depth in depths:
            MoveWheel(side, depth, dir, t, True)

    time.sleep(t)
    for side in sides:
        POWER[side].stop()

def Turn(side, dir, t):
    Move([side], ['F', 'B'], dir, t)

def Straight(dir, t):
    Move(['L', 'R'], ['F', 'B'], dir, t) 
    
### DEBUG ####

time.sleep(5)
Straight(1, 3)

MoveWheel('R', 'F', 1, 1)
MoveWheel('R', 'F', -1, 1)
MoveWheel('R', 'B', 1, 1)
MoveWheel('R', 'B', -1, 1)
Turn('R', 1, 3)

MoveWheel('L', 'F', 1, 1)
MoveWheel('L', 'F', -1, 1)
MoveWheel('L', 'B', 1, 1)
MoveWheel('L', 'B', -1, 1)
Turn('L', 1, 3)

Straight(1, 10)

# in Python, before shutdown

Cleanup()
