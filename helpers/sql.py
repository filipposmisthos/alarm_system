import MySQLdb as dbase
from helpers.time import currentDateFormatted

def connectToSqlDatabase():
     try:
          db = dbase.connect("localhost","root","root","alarm_system"); 
          cursor = db.cursor();
        
     except:
          cursor=None
          db=None
          
     return cursor,db

def getSqlLastEntryProperty(propertyName):
     
     cursor,db = connectToSqlDatabase()

     if cursor is not None:
          cursor.execute("SELECT * FROM events ORDER BY date DESC LIMIT 1");
          last_record = cursor.fetchall();
     
          if(last_record==()):
               return last_record;
          else:
               return last_record[0][
                    1 if propertyName=='code' else 3 if propertyName=='uid' else 2]

     else:
          return None

def storeSqlEntry(password,action,uid):
     
     cursor,db = connectToSqlDatabase();

     currentDatetime=currentDateFormatted("%d/%m/%Y %H:%M:%S");
     values=(currentDatetime,password,action,uid);
     cursor.execute("INSERT INTO events VALUES (%s,%s,%s,%s)",values);
     db.commit()
