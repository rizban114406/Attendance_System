import os
import time as t
from attendanceFileConfig import attendanceFileConfig
fileObject = attendanceFileConfig()

if __name__ == '__main__':
    task = fileObject.readDesiredTask()

    if task != '1':
        while 1:
            task = fileObject.readDesiredTask()
            if task == '1':
                break
            t.sleep(1)
    os.system('sudo pkill -f attendanceFingerPrint.py')
    os.system('sudo pkill -f attendanceRFIDScanner.py')
    os.system('sudo pkill -f attendanceGetFingerInfo.py')
    print "Killed Successfully"
    
