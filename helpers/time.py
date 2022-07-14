import time
import signal
from datetime import datetime

def currentDateFormatted(format):
    datetimeNow = datetime.now();
    formattedDatetimeNow = datetimeNow.strftime(format);
    return formattedDatetimeNow;

def delay(time_in_seconds):
    time.sleep(time_in_seconds);

def timeoutFunction(func,argument, timeout_duration=1,default=None):
    import signal
    
    class TimeoutError(Exception):
        pass
    
    def handler(signum,frame):
        raise TimeoutError()
    
    signal.signal(signal.SIGALRM,handler)
    signal.alarm(timeout_duration)
    
    try:
        result=func(argument)
    except TimeoutError as exc:
        result = default
        raise Exception()
    finally:
        signal.alarm(0)
    
    return result