from helpers.keypad import press_button,type_code
from firebase_admin import firestore
import RPi.GPIO as GPIO
import _thread
import uuid
from helpers.constants import firestoreInfoCollection, firestoreRecordsCollection,reedPin,pirPin,buzzerFrequencyAlarm,recordsMaxCapacity,alarm_menu_options,buzzerPin,buzzerFrequency, buzzerDutyCycle, triggeredAlarmTimeout, disarmAlarmTimeout, leaveHouseTimeout
from helpers.sql import getSqlLastEntryProperty,storeSqlEntry
from helpers.time import delay,currentDateFormatted,timeoutFunction
from helpers.connection import connectedToWeb
from helpers.screenUtils import eraseCodeDigitsOnLcd

timeout = disarmAlarmTimeout
disarmedState = 'idle'

def changePassword(lcdHandle):
    
    userId = getSqlLastEntryProperty('uid')
    userPassword = getSqlLastEntryProperty('code')
    
    lcdHandle.clear()
    
    lcdHandle.write_string('Enter current\n\rpassword : ')
    inputCode = type_code(lcdHandle,"change password");
    
    if inputCode is not None:
        if inputCode == userPassword:
            lcdHandle.clear();
            lcdHandle.write_string('Enter new\n\rpassword : ');
            inputCode = type_code(lcdHandle,"change password");
            if inputCode is not None:
                lcdHandle.clear()
                lcdHandle.write_string('Are you sure\n\rabout '+inputCode+'?')
                while True:
                    setButton = press_button()
                    if setButton is not None and setButton in ['*','#']:
                        break
                if setButton=='*':
                    return
                elif setButton == '#':
                    db = firestore.client()
                    recordsDocumentReference = db.collection(firestoreRecordsCollection).document(userId)
                    
                    lcdHandle.clear()
                    lcdHandle.write_string('Updating alarm\n\rrecords...')
                    
                    try:
                        recordsDocument = timeoutFunction(recordsDocumentReference.get,None,timeout_duration=10);
                        
                    except Exception as exc:
                        recordsDocument=None
                    
                    if recordsDocument is None:
                        lcdHandle.clear();
                        lcdHandle.write_string('Weak internet\n\rconnection.');
                        delay(3);
                        lcdHandle.clear();
                        lcdHandle.write_string('Failed to update\n\ralarm records.');
                        delay(3);
                    else:
                        currentDatetime=currentDateFormatted("%d/%m/%Y %H:%M:%S");
                                    
                        userDocumentRecs = recordsDocument.to_dict();
                        if userDocumentRecs is None:
                            lcdHandle.clear();
                            lcdHandle.write_string('Remote database\n\ris not set.')
                            delay(3)
                            lcdHandle.clear();
                            lcdHandle.write_string('Failed to update\n\ralarm records.');
                            delay(3);
                            lcdHandle.clear();
                            lcdHandle.write_string("Run 'Sync user\n\rdata' command.");
                            delay(3);
                        else:
                            userDocumentRecsList = userDocumentRecs['recs'];
                            if(len(userDocumentRecsList)==recordsMaxCapacity):
                                userDocumentRecsList.pop(0)
                            userDocumentRecsList.append({'action' : 'Password was changed from '+userPassword+' to '+inputCode,'device' : 'lcd_screen', 'time' : currentDatetime})
                            try:
                                timeoutFunction(
                                    recordsDocumentReference.update,
                                    {
                                        'recs' : userDocumentRecsList
                                    },
                                    timeout_duration=10
                                );
                            except:
                                lcdHandle.clear();
                                lcdHandle.write_string('Weak internet\n\rconnection.');
                                delay(3);
                                lcdHandle.clear();
                                lcdHandle.write_string('Failed to update\n\ralarm records.');
                                delay(3);
                    
                    lcdHandle.clear();
                    lcdHandle.write_string('Updating local\n\rdatabase...');
                    delay(3)
                    storeSqlEntry(inputCode,'change_password',userId)
                    lcdHandle.clear()
                    lcdHandle.write_string('Your new\n\rpassword : '+inputCode)
                    delay(3)
                    lcdHandle.clear()
                    return
            else:
                return
        else:
            return
    else:
        return
        

def authorizedUser(lcdHandle):
    
    userPassword = getSqlLastEntryProperty('code')
    
    lcdHandle.write_string('Welcome!');
    delay(4);
    lcdHandle.clear();
    
    
    if userPassword is None:
        lcdHandle.write_string('Local database\n\ris corrupted.');
        delay(3)
        lcdHandle.clear();
        lcdHandle.write_string('Contact the\n\ralarm system');
        delay(3)
        lcdHandle.clear();
        lcdHandle.write_string('manufacturer.');
        delay(3)
        lcdHandle.clear()
        return False
    
    elif userPassword==():
        
        set_new_user(lcdHandle)
        return True
            
    else:
        lcdHandle.write_string('Enter your\n\rpassword : ')
    
        while True:
            enteredCode = type_code(lcdHandle,'initiate alarm')
            if enteredCode==userPassword:
                break
            else:
                eraseCodeDigitsOnLcd(lcdHandle,4)
                
        lcdHandle.clear()
        lcdHandle.write_string('Password is\n\rcorrect.')
        delay(3)
        return True
        
def set_new_user(lcdHandle):
    
    userPassword = getSqlLastEntryProperty('code')

    setButton=None
    
    lcdHandle.write_string('Please, set new\n\r4 digit password')
    delay(3)
    lcdHandle.clear()
    
    while True:
        lcdHandle.write_string('Enter password:\n\r');
        enteredCode = type_code(lcdHandle,'set password')
        lcdHandle.clear()
        lcdHandle.write_string('Are you sure\n\rabout '+enteredCode+'?')
        while setButton is None or setButton not in ['*','#']:
            setButton = press_button()
        lcdHandle.clear()
        if setButton=='*':
            setButton=None
            continue
        else:
            break

    userEmail=str(enteredCode)+'@alarm.com';
    userPassword='#'+str(enteredCode)+'#';
                
    documentUid = str(uuid.uuid4())
                
    db = firestore.client()

    userDocumentReference=db.collection(firestoreInfoCollection).document(documentUid);

    lcdHandle.clear()
    lcdHandle.write_string('Initializing\n\rremote database.')
                
    try:
        timeoutFunction(
            userDocumentReference.set,
            {
                'alarm_state': 'Unarmed',
                'email': userEmail,
                'pir_sensor':'Not detecting',
                'reed_switch':'Not detecting',
                'notification_action':'None',
                'password': userPassword
            },
            timeout_duration = 10
        );
    except Exception as exc:
        lcdHandle.clear()
        lcdHandle.write_string('Remote database\n\rfailed to set.');
        delay(3)
        lcdHandle.clear()
        lcdHandle.write_string('Restore internet\n\rconnection and');
        delay(3)
        lcdHandle.clear()
        lcdHandle.write_string("run 'Sync user\n\rdata' command");
        delay(3)
        lcdHandle.clear()
        lcdHandle.write_string('to monitor the\n\ralarm system.');
    
    delay(3)
    lcdHandle.clear()
    lcdHandle.write_string('Initializing\n\rlocal database.')
    storeSqlEntry(enteredCode,'set_password',documentUid)
    delay(3)
    lcdHandle.clear()
    lcdHandle.write_string('Your new\n\rpassword : '+ enteredCode)
    delay(3)
    lcdHandle.clear()

def setAlarm(lcdHandle):
    
    userId = getSqlLastEntryProperty('uid')
    userPassword = getSqlLastEntryProperty('code')
    
    choiceIndex=0;
    buzzerHandle = GPIO.PWM(buzzerPin,1)

    lcdHandle.clear()
    lcdHandle.write_string(' '+alarm_menu_options[0]+'\n\r')
    lcdHandle.write_string(' '+alarm_menu_options[1])

    while True:
        button=''

        if choiceIndex==0:
            lcdHandle.cursor_pos = [0,0]
            lcdHandle.write_string('>')
            lcdHandle.cursor_pos = [1,0]
            lcdHandle.write_string(' ')
        else:
            lcdHandle.cursor_pos = [0,0]
            lcdHandle.write_string(' ')
            lcdHandle.cursor_pos = [1,0]
            lcdHandle.write_string('>')

        while button=='' or button is None:
            button=press_button();
            
            if button =='*':
                return;
            elif button=='5':
                if(choiceIndex>0):
                    choiceIndex-=1;
            elif button=='0':
                if(choiceIndex<1):
                    choiceIndex+=1;
            elif button=='#':
                action='None'
                while action!='correct_code_alarm_disarmed':
                
                    firestoreDbHandle = firestore.client()
                
                    alarmMode = 'inhouse' if choiceIndex==0 else 'outhouse'

                    localDbAlarmMessage = 'set alarm '+ ('inhouse' if choiceIndex==0 else 'outhouse');
                    notificationAction = alarmMode + '_mode_alarm_armed'
                
                    lcdHandle.clear();
                    '''
                    if action=='None':
                        lcdHandle.write_string(alarmMode+' mode on')
                        delay(3)
                        lcdHandle.clear()
                        lcdHandle.write_string('In case of weak\n\rconnection');
                        delay(3)
                        lcdHandle.clear();
                        lcdHandle.write_string('or unset remote\n\rdatabase,');
                        delay(3);
                        lcdHandle.clear();
                        lcdHandle.write_string("alarm records\n\rare not updated.")
                        delay(3)
                        lcdHandle.clear();
                        lcdHandle.write_string('You have '+str(leaveHouseTimeout)+' \n\rseconds to leave')
                        delay(3)
                        lcdHandle.clear()
                    
                        lcdHandle.cursor_pos = (0,1)
                        lcdHandle.write_string('  seconds left');

                        buzzerHandle.ChangeFrequency(buzzerFrequency)
                
                        for i in range(leaveHouseTimeout,-1,-1):
                            lcdHandle.cursor_pos=(0,0)
                            lcdHandle.write_string(('0' if i<10 else '')+str(i));
                            buzzerHandle.stop();
                            delay(1);
                            buzzerHandle.start(buzzerDutyCycle)
                    
                        buzzerHandle.stop()
                    '''
                
                    currentDatetime=currentDateFormatted("%d/%m/%Y %H:%M:%S");
                    recordsDocumentReference = firestoreDbHandle.collection(firestoreRecordsCollection).document(userId);
                    userDocumentReference = firestoreDbHandle.collection(firestoreInfoCollection).document(userId);
                
                    infoUpdateObject = {
                        'alarm_state':'Armed',
                        'reed_switch':'Detecting',
                        'notification_action':notificationAction
                    }
                
                    recordsUpdateObject = {
                        'action' : alarmMode.capitalize()+" mode alarm armed",
                        'device' : 'lcd_screen',
                        'time' : currentDatetime
                    }
                
                    if choiceIndex == 1:
                        infoUpdateObject['pir_sensor'] = 'Detecting'
                
                    updateAlarmRemoteDatabase(
                        {
                            'collection':firestoreInfoCollection,
                            'reference':userDocumentReference,
                            'data': infoUpdateObject
                        },
                        {
                            'collection': firestoreRecordsCollection,
                            'reference':recordsDocumentReference,
                            'data':recordsUpdateObject    
                        }
                    );
                
                    storeSqlEntry(userPassword,localDbAlarmMessage,userId)
                    lcdHandle.clear()
                    action = armed_alarm(lcdHandle,alarmMode,buzzerHandle)
                    if action!='correct_code_alarm_disarmed':
                        choiceIndex=1
                        lcdHandle.clear()
                        lcdHandle.write_string('Setting\n\routhouse mode...');
                        delay(4)
                lcdHandle.clear()
                lcdHandle.write_string(' '+alarm_menu_options[0]+'\n\r')
                lcdHandle.write_string(' '+alarm_menu_options[1])
                break
                

def armed_alarm(lcdHandle,alarmMode,buzzerHandle):

    global disarmedState;
    global timeout;

    firestoreDBHandle = firestore.client()
    
    userId = getSqlLastEntryProperty('uid')
    userPassword = getSqlLastEntryProperty('code')
    
    records_ref = firestoreDBHandle.collection(firestoreRecordsCollection).document(userId);
    info_ref = firestoreDBHandle.collection(firestoreInfoCollection).document(userId);
    
    lcdHandle.write_string('Detecting')
    
    while True:
        if(GPIO.input(reedPin)==1):
            sensorTriggered = 'reed'
            break;
            
        elif(GPIO.input(pirPin)==1 and alarmMode== 'outhouse'):
            sensorTriggered='pir'
            break;
          
        delay(0.2);
        for i in range(3):
            lcdHandle.cursor_pos=(0,len('Detecting')+i)
            lcdHandle.write_string('.');
            delay(0.2);
        lcdHandle.cursor_pos=(0,len('Detecting'))
        lcdHandle.write_string('   ');

    storeSqlEntry(userPassword,'trigger alarm',userId);
    currentDatetime = currentDateFormatted("%d/%m/%Y %H:%M:%S");
    
    infoUpdateObject = {
        'alarm_state': 'Triggered',
        'reed_switch': 'Detected movement' if sensorTriggered =='reed' else 'Not detecting',
        'pir_sensor': 'Not detecting' if sensorTriggered =='reed' else 'Detected movement',
        'notification_action': 'door_was_opened' if sensorTriggered == 'reed' else 'someone_in_the_house'
    }
    
    recordsUpdateObject = {
        'action': 'Door was opened' if sensorTriggered=='reed' else 'Someone is in the house',
        'device':'door_opened' if sensorTriggered=='reed' else 'pir_sensor',
        'time': currentDatetime
    }
    
    updateAlarmRemoteDatabase(
                    {
                        'collection':firestoreInfoCollection,
                        'reference': info_ref,
                        'data': infoUpdateObject
                    },
                    {
                        'collection': firestoreRecordsCollection,
                        'reference':records_ref,
                        'data':recordsUpdateObject
                        
                    }
                );
    
    lcdHandle.clear();
    
    lcdHandle.write_string('Alarm activated!');
    delay(3);
    lcdHandle.clear();
    lcdHandle.write_string('You have '+str(disarmAlarmTimeout-2)+' secs\n\rto enter code.');
     
    delay(2);
    lcdHandle.clear();
     
    lcdHandle.write_string('Enter code:');

    timeout = disarmAlarmTimeout;
    disarmedState = 'countdown';
    _thread.start_new_thread(firstCountdownThread,("Alarm thread",1,buzzerHandle));
    
    alarmDisarmCode = alarm_type_code(lcdHandle);
     
    lcdHandle.clear();
    
    if timeout>0:
          if(alarmDisarmCode==userPassword):
                lcdHandle.write_string('Correct code.\n\rAlarm disarmed.');
                disarmedState='idle'
                action='correct_code_alarm_disarmed'
                storeSqlEntry(userPassword,'correct code alarm disarmed',userId);
                currentDatetime = currentDateFormatted("%d/%m/%Y %H:%M:%S");
                buzzerHandle.stop()
                
                infoUpdateObject = {
                        'alarm_state': 'Unarmed',
                        'reed_switch': 'Not detecting',
                        'pir_sensor': 'Not detecting',
                        'notification_action': action
                    }
                
                recordsUpdateObject = {
                        'action': 'Correct code alarm disarmed',
                        'device':'lcd_screen',
                        'time': currentDatetime
                    }
                
                updateAlarmRemoteDatabase(
                    {
                        'collection': firestoreInfoCollection,
                        'reference': info_ref,
                        'data': infoUpdateObject
                    },
                    {
                        'collection': firestoreRecordsCollection,
                        'reference':records_ref,
                        'data':recordsUpdateObject
                        
                    }
                );
            
          else:
                    storeSqlEntry(userPassword,'wrong code alarm fired',userId)
                    disarmedState='wrong code entered'
                    storeSqlEntry(userPassword,'wrong code alarm fired',userId);
                    action = 'wrong_code_alarm_fired'
                    currentDatetime = currentDateFormatted("%d/%m/%Y %H:%M:%S");
                    
                    infoUpdateObject = {
                            'notification_action': action
                        }
                    
                    recordsUpdateObject = {
                            'action': 'Wrong code alarm fired',
                            'device':'lcd_screen',
                            'time': currentDatetime
                        }
                    
                    updateAlarmRemoteDatabase(
                    {
                        'collection': firestoreInfoCollection,
                        'reference': info_ref,
                        'data': infoUpdateObject
                    },
                    {
                        'collection': firestoreRecordsCollection,
                        'reference':records_ref,
                        'data':recordsUpdateObject
                        
                    }
                    );
                    
    else:
               if(disarmedState=='timeout'):
                    disarmedState='code timeout';
                    currentDatetime = currentDateFormatted("%d/%m/%Y %H:%M:%S");
                    storeSqlEntry(userPassword,'code timeout alarm fired',userId)
                    action = 'code_timeout_alarm_fired'
                    infoUpdateObject = {
                            'notification_action': action
                        }
                    
                    recordsUpdateObject = {
                            'action': 'Code timeout alarm fired',
                            'device':'lcd_screen',
                            'time': currentDatetime
                        }
                    
                    updateAlarmRemoteDatabase(
                    {
                        'collection': firestoreInfoCollection,
                        'reference': info_ref,
                        'data': infoUpdateObject
                    },
                    {
                        'collection': firestoreRecordsCollection,
                        'reference':records_ref,
                        'data':recordsUpdateObject
                        
                    }
                );
                    
                    
    if(disarmedState!='idle'):
        action = alarmSound(lcdHandle,buzzerHandle);

    timeout = 0
    disarmedState = 'idle'
    delay(5)
    return action
    

def alarmSound(lcdHandle,buzzerHandle):
    global timeout;
    global disarmedState;
    
    if(disarmedState!='wrong code entered'):
        disarmedState = 'countdown'
        
    timeout=triggeredAlarmTimeout;
    #buzzerHandle.ChangeFrequency(buzzerFrequencyAlarm)
    
    _thread.start_new_thread(secondCountdownThread,("Alarm thread",1,buzzerHandle));
    lcdHandle.clear();
    firestoreDBHandle = firestore.client()
    userId = getSqlLastEntryProperty('uid')
    userPassword = getSqlLastEntryProperty('code')
    records_ref = firestoreDBHandle.collection(firestoreRecordsCollection).document(userId);
    info_ref=firestoreDBHandle.collection(firestoreInfoCollection).document(userId);
    
    lcdHandle.write_string('Alarm fired!\n\rEnter code:');
    
    while True:
     
        triggeredAlarmCode = alarm_type_code(lcdHandle)
     
        if timeout>0:
            if(triggeredAlarmCode == userPassword):
                disarmedState='idle';
                lcdHandle.clear()
                lcdHandle.write_string('Correct code.\n\rAlarm disarmed.');
                storeSqlEntry(userPassword,'correct code alarm disarmed',userId)
                notification_action='correct_code_alarm_disarmed';
                currentDatetime = currentDateFormatted("%d/%m/%Y %H:%M:%S");
                
                recordsUpdateObject = {
                        'action': 'Correct code alarm disarmed',
                        'device':'lcd_screen',
                        'time': currentDatetime
                    }
                
                break;
            else:
                eraseCodeDigitsOnLcd(lcdHandle,4)
               
        else:
            disarmedState='idle';
            lcdHandle.clear()
            lcdHandle.write_string('Alarm timeout.\n\rAlarm disarmed.');
            storeSqlEntry(userPassword,'alarm timeout disarmed',userId)
            notification_action='alarm_timeout_alarm_disarmed'
            currentDatetime = currentDateFormatted("%d/%m/%Y %H:%M:%S");
            
            recordsUpdateObject = {
                    'action': 'Timeout alarm disarmed',
                    'device':'lcd_screen',
                    'time': currentDatetime
                }
            
            break;
        
    infoUpdateObject= {
            'alarm_state': 'Unarmed',
            'reed_switch': 'Not detecting',
            'pir_sensor':'Not detecting',
            'notification_action' : notification_action
        }
    
    updateAlarmRemoteDatabase(
                    {
                        'collection': firestoreInfoCollection,
                        'reference': info_ref,
                        'data': infoUpdateObject
                    },
                    {
                        'collection':firestoreRecordsCollection,
                        'reference':records_ref,
                        'data':recordsUpdateObject
                        
                    }
    )
    
    
    
    disarmedState='idle';
    timeout=0
    return notification_action


def alarm_type_code(lcdHandle):

    inputCode=''

    pressed_button= ''

    while(timeout>0 or disarmedState=='countdown'):
        
        pressed_button = press_button()
            
        if pressed_button=='*':
            if len(inputCode)>0:
                    inputCode = inputCode[:-1];
                    new_lcd_cursor_pos = (lcdHandle.cursor_pos[0],lcdHandle.cursor_pos[1]-1);
                    lcdHandle.cursor_pos = new_lcd_cursor_pos;
                    lcdHandle.write_string(' ');
                    lcdHandle.cursor_pos = new_lcd_cursor_pos;

        elif pressed_button=='#':
            if len(inputCode)==4:
                return inputCode
                    
        else:
            if len(inputCode)<4 and pressed_button is not None:
                inputCode += pressed_button;
                lcdHandle.write_string(pressed_button);

def updateAlarmRemoteDatabase(infoConfigDocument,recordsConfigDocument):
    _thread.start_new_thread(firestoreUpdateThread,(
                    infoConfigDocument['collection'],
                    infoConfigDocument['reference'],
                    infoConfigDocument['data']
                ));
                
    _thread.start_new_thread(firestoreUpdateThread,(
                    recordsConfigDocument['collection'],
                    recordsConfigDocument['reference'],
                    recordsConfigDocument['data']
                ));

def firestoreUpdateThread(collectionName,documentReference,updateObject):
    if(connectedToWeb(1)):
        resultDocument=documentReference.get();
        resultDocumentDict = resultDocument.to_dict();
        if resultDocumentDict is not None:
            if collectionName==firestoreRecordsCollection:
                recordsDocumentList = resultDocumentDict['recs'];
                if(len(recordsDocumentList)==recordsMaxCapacity):
                    recordsDocumentList.pop(0);
                recordsDocumentList.append(updateObject);
                try:
                    documentReference.update({'recs': recordsDocumentList});
                except:
                    pass
            elif collectionName==firestoreInfoCollection:
                try:
                    documentReference.update(updateObject);
                except:
                    pass

def firstCountdownThread(thread_name,delaySeconds,buzzerHandle):
     global timeout;
     global disarmedState;
     
     while(disarmedState not in ['idle','wrong code entered','code timeout'] and timeout>0):
               delay(0.01)
               timeout-=1;
               if timeout==0:
                    disarmedState='timeout';
                    return
               buzzerHandle.stop()
               delay(delaySeconds);
               buzzerHandle.start(buzzerDutyCycle)
     if disarmedState=='idle':
         buzzerHandle.stop()
                     
def secondCountdownThread(thread_name,delaySeconds,buzzerHandle):
     global timeout;
     global disarmedState;
     
     while(disarmedState!='idle' or timeout>0):
               
               delay(0.01)
               timeout-=1;
               if timeout==0:
                    disarmedState='timeout';
               delay(delaySeconds)
               
     buzzerHandle.stop()