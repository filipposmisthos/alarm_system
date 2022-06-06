from helpers.screenUtils import handleMenuChoices
from helpers.alarm import setAlarm,changePassword
from helpers.keypad import press_button
from helpers.constants import initial_menu_options
from helpers.firestore import syncFirestoreData


def startMenu(lcdHandle):
    
    lcdHandle.clear()
    
    choiceIndex=0;
    showingLowerMenu=False;
    lcdHandle.write_string(' '+initial_menu_options[0]+'\n\r')
    lcdHandle.write_string(' '+initial_menu_options[1])
    
    while(True):
        button="";
        
        if showingLowerMenu:
            lcdHandle.cursor_pos = (0,0)
            lcdHandle.write_string('>' if choiceIndex==1 else ' ')
            lcdHandle.cursor_pos = (1,0)
            lcdHandle.write_string(' ' if choiceIndex==1 else '>')
        else:
            lcdHandle.cursor_pos = (0,0)
            lcdHandle.write_string(' ' if choiceIndex==1 else '>')
            lcdHandle.cursor_pos = (1,0)
            lcdHandle.write_string('>' if choiceIndex==1 else ' ')

        while(button=="" or button is None):
            
            button=press_button();
            
            if button in ['0','5']:
                choiceIndex,showingLowerMenu,menuAction = handleMenuChoices(button,choiceIndex,showingLowerMenu,lcdHandle);
                
                if menuAction!='none':
                    lcdHandle.clear()
                    lcdHandle.write_string(
                        ' '+initial_menu_options[0 if menuAction=='show_upper_choices' else 1]+'\n\r'
                    );
                    lcdHandle.write_string(
                        ' '+initial_menu_options[1 if menuAction=='show_upper_choices' else 2]+'\n\r'
                    );
                    break;
                
            elif button=='#':
                if choiceIndex==0:
                    changePassword(lcdHandle)
                    lcdHandle.clear()
                    lcdHandle.write_string(' '+initial_menu_options[0]+'\n\r')
                    lcdHandle.write_string(' '+initial_menu_options[1])
                
                elif(choiceIndex==1):
                    setAlarm(lcdHandle);
                    lcdHandle.clear()
                    if showingLowerMenu:
                        lcdHandle.write_string(' '+initial_menu_options[1]+'\n\r')
                        lcdHandle.write_string(' '+initial_menu_options[2])
                    else:
                        lcdHandle.write_string(' '+initial_menu_options[0]+'\n\r')
                        lcdHandle.write_string(' '+initial_menu_options[1])
                        
                elif choiceIndex==2:
                    lcdHandle.clear()
                    syncFirestoreData(lcdHandle)
                    lcdHandle.clear()
                    lcdHandle.write_string(' '+initial_menu_options[1]+'\n\r')
                    lcdHandle.write_string(' '+initial_menu_options[2])
                    
