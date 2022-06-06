import RPi.GPIO as GPIO
from helpers.constants import keypadRowPins,keypadColumnPins,lcdRowCount,lcdColumnCount,reedPin,pirPin,buzzerPin,rsPin,ePin,dataPins
from RPLCD import CharLCD

def configureLcd():
    GPIO.setwarnings(False);
    GPIO.setmode(GPIO.BCM);
    
    for columnPin in keypadColumnPins:
        GPIO.setup(columnPin,GPIO.OUT);
        GPIO.output(columnPin,1);

    for rowPin in keypadRowPins:
        GPIO.setup(rowPin,GPIO.IN,pull_up_down=GPIO.PUD_UP);
   
    GPIO.setup(reedPin,GPIO.IN,pull_up_down=GPIO.PUD_UP);
    GPIO.setup(pirPin,GPIO.IN,pull_up_down=GPIO.PUD_UP);

    GPIO.setup(buzzerPin,GPIO.OUT);
    
    return CharLCD(
        numbering_mode = GPIO.BCM,
        cols = lcdColumnCount,
        rows = lcdRowCount,
        pin_rs = rsPin,
        pin_e = ePin,
        pins_data = dataPins,
        compat_mode = True
    );