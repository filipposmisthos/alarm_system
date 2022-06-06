from helpers.lcd import configureLcd
from helpers.firebase import initializeFirebase
from helpers.alarm import authorizedUser
from startMenu import startMenu

lcdHandle = configureLcd()

initializeFirebase()

userIsAuthorized = authorizedUser(lcdHandle);
#userIsAuthorized = True

if userIsAuthorized:
    startMenu(lcdHandle)
