import datetime
from pyfingerprint.pyfingerprint import PyFingerprint
import MySQLdb
import time as t
import RPi.GPIO as GPIO
import sys
from attendanceDatabaseConfig import attendanceDatabaseConfig
from attendanceKeypad import attendanceKeypad
from attendanceLCDPrint import attendanceLCDPrint
from attendanceFileConfig import attendanceFileConfig
from attendanceAllAPI import attendanceAllAPI
#import picamera
GPIO.setmode(GPIO.BCM)
GPIO.setup(20, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)

apiObject = attendanceAllAPI()
fileObject = attendanceFileConfig()
lcdPrint = attendanceLCDPrint()
keyPress = attendanceKeypad()
dbObject = attendanceDatabaseConfig()
database = dbObject.connectDataBase()

def configureFingerPrint():
    while True:
        try:
            f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)
            if ( f.verifyPassword() == False ):
                raise ValueError('The given fingerprint sensor password is wrong!')
                t.sleep(2)

            else:
                break
        except Exception as e:
            #lcdPrint.printExceptionMessage(str(e))
            fileObject.updateExceptionMessage("attendanceFingerPrint{configureFingerPrint}",str(e))
            #t.sleep(1)
            sys.exit()    
    return f

def createNewTemplateToSync(f,employeeInfo):
    x = str(employeeInfo[5]).split('-')
    characteristics = []
    for i in range(0,len(x)-1):
        characteristics.append(int(x[i]))
    f.uploadCharacteristics(0x01,characteristics)
    f.storeTemplate(int(employeeInfo[4]),0x01)
    import re
    sp = re.split(' |-|',str(employeeInfo[1]))
    if(len(sp) == 2):
        employee = sp[1]
    else:
        employee = sp[0]

    dbObject.insertNewEmployee(employeeInfo[1], \
                               employeeInfo[2], \
                               employeeInfo[3], \
                               employeeInfo[4], \
                               employeeInfo[5], \
                               employeeInfo[7], \
                               employee, \
                               database)
    dbObject.deleteFromTempTableToSync(employeeInfo[2],employeeInfo[7],database)
        

def updateListOfUsedTemplates(f):
    tableIndex1 = f.getTemplateIndex(0)
    tableIndex2 = f.getTemplateIndex(1)
    tableIndex3 = f.getTemplateIndex(2)
    tableIndex4 = f.getTemplateIndex(3)
    index = []
    for i in range(0, len(tableIndex1)):
        index.append(tableIndex1[i])
        #print('Template at position #' + str(i) + ' is used: ' + str(tableIndex[i]))
    for i in range(0, len(tableIndex2)):
        index.append(tableIndex2[i])
    for i in range(0, len(tableIndex3)):
        index.append(tableIndex3[i])
    for i in range(0, len(tableIndex4)):
        index.append(tableIndex4[i])
    storedIndex = ""
    for i in range(0, len(index)):
        if (str(index[i]) == "True"):
            storedIndex = storedIndex + str(i) + '-'
    fileObject.updateStoredIndex(storedIndex)
    
def syncWithOtherDevices(f):
    lcdPrint.printSyncMessage()
    try:
        getDataToDelete = dbObject.getInfoFromTempTableToDelete(database)
        getDataToSync = dbObject.getInfoFromTempTableToEnrollOrUpdate(database)
        if (getDataToDelete != "Synced"):
            for reading in getDataToDelete.fetchall():
                prevId = dbObject.checkEmployeeInfoTableToDelete(reading[0],reading[1],database)
                f.deleteTemplate(prevId)
                dbObject.deleteFromEmployeeInfoTable(reading[0],reading[1],database)
                dbObject.deleteFromTempTableToSync(reading[0],reading[1],database)
                t.sleep(.3)                                 
        if (getDataToSync != "Synced"):
            for reading in getDataToSync.fetchall():
                prevId = dbObject.checkEmployeeInfoTableToDelete(reading[2],reading[7],database)
                if prevId > 0:
                    f.deleteTemplate(prevId)
                    dbObject.deleteFromEmployeeInfoTable(reading[2],reading[7],database)
                createNewTemplateToSync(f,reading)
                t.sleep(.3)
            print "Device Is Fully Synced With The Server"
        else:
            print "Device Is Already Synced With The Server"
        updateListOfUsedTemplates(f)
    except Exception as e:
        fileObject.updateExceptionMessage("attendanceFingerPrint{syncWithOtherDevices}",str(e))
        fileObject.updateCatTask('1')
        dbObject.databaseClose(database)
        sys.exit()

def createEventLogg(f,currentDateTime,currentTime):
    try:
    	f.convertImage(0x01)
        result = f.searchTemplate()
        positionNumber = result[0]
        accuracyScore = result[1]
        print positionNumber
        if (positionNumber == -1):
            GPIO.output(21, 1)
            lcdPrint.printIfNoMatchFound()
            GPIO.output(21, 0)
        else :
            #print positionNumber
            employeeDetails = dbObject.getEmployeeDetails(positionNumber,database)
            #print employeeDetails

            if employeeDetails != '0':
                GPIO.output(20, 1)
                dbObject.insertEventTime(employeeDetails[1], \
                                         positionNumber, \
                                         currentDateTime, \
                                         '1', \
                                         employeeDetails[3], \
                                         database)
                lcdPrint.printAfterSuccessfullEventLogg(currentTime,employeeDetails)
                GPIO.output(20, 0)
            else:
                f.deleteTemplate(positionNumber)
                lcdPrint.printAfterSuccessfullEventLoggButNoEmployeeID()
    except Exception as e:
        fileObject.updateExceptionMessage("attendanceFingerPrint{createEventLogg}",str(e))
        #lcdPrint.printExceptionMessage(str(e))
            
def calculateTimeDifference(currentDateTime,timeLimit):
    NowTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    diffStart = (datetime.datetime.strptime(str(NowTime), '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(str(currentDateTime), '%Y-%m-%d %H:%M:%S'))
    if(diffStart.seconds > timeLimit):
        return 1
    else:
        return 0
    
def digit(currentDateTime,timeLimit):
    # Loop while waiting for a keypress
    r = None
    x = 0
    while 1:
        r = keyPress.getKey()
        x = calculateTimeDifference(currentDateTime,timeLimit)
        if r != None or x == 1:
            break
    if(r == None):
        return "K"
    else:
        return r
    
#####################################Enrollment Process################################
def getPasswordToEnroll(currentDateTime):
    lcdPrint.printEnrollemntGivePassword()
    ch = ""
    password = ""
    x = 0
    while 1:
        ch = digit(currentDateTime,150)
        if ((ch == 1 or ch == 2 or ch == 3 or ch == 4 or ch == 5 or ch == 6 or ch == 7 or ch == 8 or ch == 9 or ch == 0) and (len(password) <= 9)):
            password = password + str(ch)
            lcdPrint.printPassword('*')
        elif ( ch == 'A'):
            break
        elif ( ch == 'B' and len(password) != 0):
            lcdPrint.setLCDCursorForBackSpace((len(password)+9),1)
            password = password[:-1]
        elif ( ch == 'C' or ch == 'K' or x == 1):
            password = ""
            x = 1
            break
        x = calculateTimeDifference(currentDateTime,150)
        t.sleep(.7)
    if x == 1 or ch == 'C':
        lcdPrint.printPasswordNotGivenOrTimeOutOrCanceled(ch," ",x)
        return "Time Out"
    else:
        return password
def selectCompanyToEnroll(currentDateTime):
    ch = ""
    x = 0
    allCompany = dbObject.getAllCompanyList(database)
    companyList = []
    companyID = []
    selectedCompany = 0
    for company in allCompany.fetchall():
        companyID.append(company[0])
        companyList.append(company[1])
    startIndex = []
    printedCompany = []
    previousPrintedIndex = 0
    pageNo = 0
    startIndex.append(0)
    printedCompany.append(0)
    while 1:
        previousPrintedIndex = lcdPrint.printCompanyNames(companyList[startIndex[pageNo]:len(companyID)],printedCompany[pageNo])
        ch = digit(currentDateTime,150)
        if (ch == 1 or ch == 2 or ch == 3 or ch == 4 or ch == 5 or ch == 6 or ch == 7 or ch == 8 or ch == 9):
            if (int(ch) <= (previousPrintedIndex - printedCompany[pageNo])):
                selectedCompany = int(companyID[int(ch)-1+printedCompany[pageNo]])
                break
        elif (ch == 'K' or x == 1):
            selectedCompany = 0
            x == 1
            break
        elif (ch == 'C'):
            selectedCompany = 0
            break
        elif (ch == 'D'):        
            if (previousPrintedIndex < len(companyID)):
                pageNo = pageNo + 1
                startIndex.append(previousPrintedIndex)
                printedCompany.append(previousPrintedIndex)
        elif (ch == '*'):
            if pageNo > 0:
                startIndex.pop(pageNo)
                printedCompany.pop(pageNo)
                pageNo = pageNo - 1
        x = calculateTimeDifference(currentDateTime,150)
        t.sleep(.7)

    if x == 1 or ch == 'C':
        lcdPrint.printCompanyNotSelected(ch,x)
        return 0
    else:
        return selectedCompany

def getEmployeeIdToEnroll(currentDateTime):
    lcdPrint.printEnrollemntGiveEmployeeId()
    ch = ""
    employeeId = ""
    x = 0
    while 1:
        ch = digit(currentDateTime,150)
        if ((ch == 1 or ch == 2 or ch == 3 or ch == 4 or ch == 5 or ch == 6 or ch == 7 or ch == 8 or ch == 9 or ch == 0) and (len(employeeId) <= 4)):
            employeeId = employeeId + str(ch)
            lcdPrint.printEmployeeId(ch)
        elif ( ch == 'A'):
            break
        elif ( ch == 'B' and len(employeeId) != 0):
            lcdPrint.setLCDCursorForBackSpace((len(employeeId)+11),1)
            employeeId = employeeId[:-1]
        elif ( ch == 'C' or ch == 'K' or x == 1):
            employeeId = ""
            x = 1
            break
        x = calculateTimeDifference(currentDateTime,150)
        t.sleep(.7)
    if x == 1 or ch == 'C':
        lcdPrint.printIDNotGivenOrTimeOutOrCanceled(ch," ",x)
        return "Time Out"
    else:
        return employeeId

def takeFingerprintToEnroll(f,currentDateTime):
    x = 0 
    lcdPrint.printPutAnyFinger()
    while ( f.readImage() == False and x == 0):
        x = calculateTimeDifference(currentDateTime,150)
        t.sleep(1)
        pass
    if (x != 1):
        f.convertImage(0x01)
        result = f.searchTemplate()
        positionNumber = result[0]
        if ( positionNumber >= 0 ):
            lcdPrint.printFingerAlreadyExists()
        else:
            lcdPrint.printRemoveAndPutSameFinger()
            while ( f.readImage() == False and x == 0):
                x = calculateTimeDifference(currentDateTime,150)
                t.sleep(1)
                pass
            if x != 1:
                lcdPrint.printWaitAfterGivingBothFingers()
                f.convertImage(0x02)
                if ( f.compareCharacteristics() == 0):
                    lcdPrint.printTwoFingersDidNotMatched()
                    return 0
                else:
                    return 1
            else:
                lcdPrint.timeOutMessage()
                return 0
        
    else:
        lcdPrint.timeOutMessage()
        return 0
def createNewTemplate(f,uniqueId,selectedCompany,employeeId,deviceId):
    characterMatrix = f.downloadCharacteristics()
    matrix = ""
    for i in characterMatrix:
        matrix = matrix+ str(i)+ "-"
        
    receivedData = apiObject.getFingerId(uniqueId,matrix,selectedCompany,deviceId)
    # print receivedData
    if receivedData != "no" and receivedData != "Server Error":
        f.storeTemplate(int(receivedData[3]),0x01)
        dbObject.insertNewEmployee(receivedData[0], \
                                   receivedData[1], \
                                   receivedData[2], \
                                   receivedData[3], \
                                   matrix, \
                                   selectedCompany, \
                                   employeeId, \
                                   database)
        # print("new Template")
        return "1"
    else:
        return receivedData
        
def enrollNewEmployee(f,currentDateTime,deviceId):
    x = 0
    try:
        maintainanceStatus = fileObject.readConfigUpdateStatus()
        if maintainanceStatus == '1':
            enteredPassword = getPasswordToEnroll(currentDateTime)
            if (enteredPassword != "Time Out" and len(enteredPassword) != 0):
                severCheckPassword = apiObject.authenticatePassword(enteredPassword,deviceId)
                t.sleep(.5)
                if (severCheckPassword == "Matched"):
                    selectedCompany = selectCompanyToEnroll(currentDateTime)
                    t.sleep(.8)
                    if selectedCompany > 0:
                        employeeId = getEmployeeIdToEnroll(currentDateTime)
                        if (employeeId != "Time Out" and len(employeeId) != 0):
                            localCheck = dbObject.checkEmployeeInfoTable(employeeId,selectedCompany,database)
                            #print localCheck
                            x = calculateTimeDifference(currentDateTime,150)
                            if (localCheck != "Registered"):
                                serverCheck = apiObject.checkServerStatus(employeeId,selectedCompany)
                                #print serverCheck
                                if (serverCheck != "Registered" and serverCheck != "Invalid" and serverCheck != "Server Down" and x != 1):
                                    uniqueId = int(serverCheck)
                                    fingerInput = takeFingerprintToEnroll(f,currentDateTime)
                                    if fingerInput == 1 :
                                        status = createNewTemplate(f,uniqueId,selectedCompany,employeeId,deviceId)
                                        if status == "1":
                                            lcdPrint.printSuccessEnrollmentMessage()
                                        else:
                                            lcdPrint.printUnsuccessEnrollmentMessage(status)                                                 
                                else:
                                    lcdPrint.printValidEmployeeNotSuccess(serverCheck,employeeId,x)
                            else:
                                lcdPrint.printValidEmployeeNotSuccess(localCheck,employeeId,x)
                        elif len(employeeId) == 0:
                            lcdPrint.printIDNotGivenOrTimeOutOrCanceled("","",x)
                else:
                    lcdPrint.printPasswordResponse(severCheckPassword,x)
            elif len(enteredPassword) == 0:
                lcdPrint.printPasswordNotGivenOrTimeOutOrCanceled("","",x)
        else:
            lcdPrint.printDeviceMaintanace()
    except Exception as e:
         lcdPrint.printExceptionMessage(str(e))
         fileObject.updateExceptionMessage("attendanceFingerPrint{enrollNewEmployee}",str(e))
#####################################Enrollment Process################################
         
if __name__ == '__main__':
    deviceId = dbObject.getDeviceId(database)
    if deviceId != 0:
        f = configureFingerPrint()
        fileObject.updateCatTask('4')
        syncWithOtherDevices(f)
        fileObject.updateCatTask('1')
        isFingerPrintUsed = 1

        while True:
            try:
                if isFingerPrintUsed == 1:
                    lcdPrint.printInitialMessage()
                desiredTask = '1'
                while (f.readImage() == False):
                    desiredTask = fileObject.readDesiredTask()
                    if (desiredTask != '1') :
                        break
                    t.sleep(.8)
                if desiredTask == '1':
                    fileObject.updateCatTask('6')
                    
                elif desiredTask == '7':
                    #isFingerPrintUsed = 0
                    t.sleep(2)   
                nowTime = datetime.datetime.now()
                currentTime = nowTime.strftime('%H:%M:%S')
                currentDateTime = nowTime.strftime('%Y-%m-%d %H:%M:%S')
                
                desiredTask = fileObject.readDesiredTask()
                if desiredTask == '6' :
                    lcdPrint.printPleaseWait()
                    createEventLogg(f,currentDateTime,currentTime)
                    fileObject.updateCatTask('1')
                    isFingerPrintUsed = 1

                elif desiredTask == '2':
                    lcdPrint.printPleaseWait()
                    enrollNewEmployee(f,currentDateTime,deviceId)
                    fileObject.updateCatTask('1')
                    isFingerPrintUsed = 1

            except Exception as e:
                fileObject.updateCatTask('1')
                fileObject.updateExceptionMessage("attendanceFingerPrint{__main__}",str(e))
                lcdPrint.printExceptionMessage(str(e))
                dbObject.databaseClose(database)
                sys.exit()
