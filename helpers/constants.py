credentials_path = './alarm-system-b93b7-firebase-adminsdk-1eo5n-af6b55186a.json'

firestoreInfoCollection = 'info'
firestoreRecordsCollection = 'records'

keypadRowPins=[14,22,27,18]
keypadColumnPins=[15,4,17]
dataPins=[10,9,11,25]
lcdRowCount = 2
lcdColumnCount = 16
reedPin=26
pirPin=20
buzzerPin = 5
rsPin=23
ePin=24

keypadButtonMapping = [
        ['1','2','3'],
        ['4','5','6'],
        ['7','8','9'],
        ['*','0','#']
    ]

initial_menu_options = ['Change Password','Set Alarm','Sync user data']

alarm_menu_options = ['In House Mode','Out House Mode']



#leaveHouseTimeout = 5# actual timeout seconds
leaveHouseTimeout = 1

buzzerFrequency = 750

buzzerFrequencyAlarm = 950

buzzerDutyCycle = 50

#disarmAlarmTimeout = 22 # actual timeout seconds + 2
disarmAlarmTimeout= 7
#triggeredAlarmTimeout = 21 # actual timeout seconds + 1
triggeredAlarmTimeout = 6

recordsMaxCapacity = 10
