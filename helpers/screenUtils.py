def eraseCodeDigitsOnLcd(lcdHandle,digitsCount):
    new_cursor_position = (lcdHandle.cursor_pos[0],lcdHandle.cursor_pos[1]-digitsCount)
    lcdHandle.cursor_pos=new_cursor_position
    lcdHandle.write_string(' '*digitsCount);
    lcdHandle.cursor_pos=new_cursor_position

def handleMenuChoices(button,choiceIndex,showingLowerMenu,lcdHandle):

    menuAction = 'none'
    
    if(button=='5'):
        if(choiceIndex>0):
            choiceIndex-=1;
            if showingLowerMenu:
                if choiceIndex == 0:
                    showingLowerMenu=False;
                    menuAction='show_upper_choices'
                  
    elif(button=='0'):
        if choiceIndex<2:
            choiceIndex+=1
            if not showingLowerMenu:
                if choiceIndex==2:
                    showingLowerMenu=True;
                    menuAction = 'show_lower_choices'

    return choiceIndex,showingLowerMenu,menuAction