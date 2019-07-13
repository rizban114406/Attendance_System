import time as t
from attendanceKeypad import attendanceKeypad
from attendanceFileConfig import attendanceFileConfig
from attendanceLCDPrint import attendanceLCDPrint
lcdPrint = attendanceLCDPrint()
keypress = attendanceKeypad()
fileObject = attendanceFileConfig()

def digit():
    # Loop while waiting for a keypress
    r = None
    while 1:
        lcdPrint.printInitialMessage()
        r = keypress.getKey()
        if r != None or fileObject.readDesiredTask() != '1':
            break
        t.sleep(.2)
    return r

if __name__ == '__main__':
    command = '1'
    fileObject.updateCatTask('1')
    while True:
      try:
        ch = digit()
        print ch
        if (ch == '#'):
            fileObject.updateCatTask('2')
            #print "enroll mode"
            while 1:
                task = fileObject.readDesiredTask()
                if task == '1':
                    break
                else:
                    pass
                t.sleep(1)
        else:
            while (fileObject.readDesiredTask() != '1'):
                t.sleep(.5)
        t.sleep(1)
      except Exception as e:
          #print str(e)
          fileObject.updateExceptionMessage("attendanceCommand",str(e))
          t.sleep(5)
