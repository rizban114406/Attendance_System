import serial
import RPi.GPIO as GPIO
import datetime
import sys
import time as t
from attendanceDatabaseConfig import attendanceDatabaseConfig
from attendanceLCDPrint import attendanceLCDPrint
from attendanceFileConfig import attendanceFileConfig
fileObject = attendanceFileConfig()
lcdPrint = attendanceLCDPrint()
dbObject = attendanceDatabaseConfig()
database = dbObject.connectDataBase()
GPIO.setmode(GPIO.BCM)
GPIO.setup(20, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)

def readFromRFIDScanner():
    ser = serial.Serial("/dev/serial0")
    try:
        ser.baudrate = 9600
        readID = ser.read(11)
        ser.close()
        #print readID
        readID = readID.replace("\x02", "" )
        readID = readID.replace("\x03", "" )
        #print readID[2:10]
        return readID[2:10]
    except Exception,e:
        ser.close()
        lcdPrint.printExceptionMessage(str(e))
        fileObject.updateExceptionMessage("attendanceRFIDScanner{readFromRFIDScanner}",str(e))
        return "NA"
    
def createEventLogg(employeeCardNumber,currentDateTime,currentTime):
    employeeDetails = dbObject.getEmployeeDetailsFromCard(employeeCardNumber,database)
    if employeeDetails == '0':
        GPIO.output(21, 1)
        dbObject.insertEventTime("0",\
                                 employeeCardNumber,\
                                 currentDateTime,\
                                 '2',\
                                 '0',
                                 database)
        lcdPrint.printIfNoMatchFound()
        GPIO.output(21, 0)
    else :
        dbObject.insertEventTime(employeeDetails[1],\
                                 employeeCardNumber,\
                                 currentDateTime,\
                                 '2',\
                                 employeeDetails[3],\
                                 database)
        GPIO.output(20, 1)
        lcdPrint.printAfterSuccessfullEventLogg(currentTime,employeeDetails)
        GPIO.output(20, 0)

if __name__ == '__main__':
    isRFUsed = 1
    while True:
        try:
            task = fileObject.readDesiredTask()
            if task == '1' and isRFUsed == 1:
                lcdPrint.printInitialMessage()
            rfScannerValue = readFromRFIDScanner()
            desiredTask = fileObject.readDesiredTask()
            if desiredTask == '6':
                isRFUsed = 0
                t.sleep(4)
            elif desiredTask == '2':
                isRFUsed = 0
                t.sleep(4)
            elif desiredTask == '1':    
                employeeCardNumber = int(rfScannerValue,16)
                # print employeeCardNumber
                if employeeCardNumber > 0 and  len(str(employeeCardNumber)) < 9:
                    fileObject.updateCatTask('7')
                    nowTime = datetime.datetime.now()
                    currentTime = nowTime.strftime('%H:%M:%S') #time
                    currentDateTime = nowTime.strftime('%Y-%m-%d %H:%M:%S')
                    createEventLogg(employeeCardNumber,currentDateTime,currentTime)
                    fileObject.updateCatTask('1')
                    isRFUsed = 0
            else:
                print "Device is Busy"
        except Exception as e:
            print('Exception message: ' + str(e))
            fileObject.updateExceptionMessage("attendanceRFIDScanner{__main__}",str(e))
            dbObject.databaseClose(database)
            #lcdPrint.printExceptionMessage(str(e))
            sys.exit()

            
