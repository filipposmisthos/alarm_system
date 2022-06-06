import RPi.GPIO as GPIO
import time
from helpers.constants import keypadButtonMapping,keypadRowPins,keypadColumnPins
from helpers.screenUtils import eraseCodeDigitsOnLcd

def press_button():
    
    for j in range(len(keypadColumnPins)):
        GPIO.output(keypadColumnPins[j],0);

        for i in range(len(keypadRowPins)):
            if GPIO.input(keypadRowPins[i])==0:
                output=keypadButtonMapping[i][j];
                time.sleep(0.3)
                while(GPIO.input(keypadRowPins[i])==0):
                    pass;
                    
                return output;
                    
        GPIO.output(keypadColumnPins[j],1)

def type_code(lcdHandle,action):
    
    inputCode = ''
    
    while True:
        
        pressed_button = press_button()
        
        if pressed_button=='*':
            if len(inputCode)==0:
                if action == 'change password':
                    return None
            else:
                if len(inputCode)>0:
                    inputCode = inputCode[:-1];
                    eraseCodeDigitsOnLcd(lcdHandle,1)
        elif pressed_button == '#':
            if len(inputCode)==4:
                return inputCode
        else:
            if len(inputCode)<4 and pressed_button is not None:
                inputCode += pressed_button;
                lcdHandle.write_string(pressed_button);
