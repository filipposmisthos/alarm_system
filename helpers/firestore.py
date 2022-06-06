from firebase_admin import credentials,firestore,auth,instance_id,messaging
from helpers.sql import getSqlLastEntryProperty
from helpers.time import delay,timeoutFunction
from helpers.constants import firestoreInfoCollection

def syncFirestoreData(lcdHandle):
    lcdHandle.write_string('Syncing user\n\rdata...');
    delay(3)
    firestoreDB = firestore.client()
    uid = getSqlLastEntryProperty('uid')
    userDocumentReference = firestoreDB.collection(firestoreInfoCollection).document(uid);
        
    try:
        userDocument = timeoutFunction(userDocumentReference.get,None,timeout_duration=10)
    except:
        userDocument = None
            
    if userDocument is None:
        lcdHandle.clear();
        lcdHandle.write_string('Weak internet\n\rconnection.');
        delay(3);
        lcdHandle.clear()
        lcdHandle.write_string('Cannot sync user\n\rdata.');
    else:
        localDbPassword = getSqlLastEntryProperty('code')
        firestoreEmail = str(localDbPassword)+'@alarm.com';
        firestorePassword = '#'+str(localDbPassword)+'#';
        lcdHandle.clear();
        lcdHandle.write_string('Initializing\n\rremote database.')
                
        try:
            timeoutFunction(
                userDocumentReference.set,
                {
                    'alarm_state': 'Unarmed',
                    'email': firestoreEmail,
                    'pir_sensor':'Not detecting',
                    'reed_switch':'Not detecting',
                    'notification_action':'None',
                    'password': firestorePassword
                },
                timeout_duration=10
            );
            lcdHandle.clear()
            lcdHandle.write_string('User data has\n\rbeen synced.');
                    
        except Exception as exc:
            lcdHandle.clear();
            lcdHandle.write_string('Weak internet\n\rconnection.');
            delay(3);
            lcdHandle.clear()
            lcdHandle.write_string('Cannot sync user\n\rdata.');
                    
    delay(3);