from pyfingerprint.pyfingerprint import PyFingerprint
from attendanceDatabaseConfig import attendanceDatabaseConfig
import time as t
import re
from attendanceFileConfig import attendanceFileConfig
fileObject = attendanceFileConfig()
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
            fileObject.updateExceptionMessage("attendanceFullSync{configureFingerPrint}",str(e))
            sys.exit()    
    return f

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
    
def createNewTemplate(f,employeeInfo):
    x = str(employeeInfo[5]).split('-')
    characteristics = []
    for i in range(0,len(x)-1):
        characteristics.append(int(x[i]))
    f.uploadCharacteristics(0x01,characteristics)
    f.storeTemplate(int(employeeInfo[4]),0x01)
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
    
def syncWithOtherDevices(f):
    try:
        getDataToSync = dbObject.getInfoFromTempTableToEnrollOrUpdate(database)
        getDataToDelete = dbObject.getInfoFromTempTableToDelete(database)
        
        if (getDataToDelete != "Synced"):
            count = 0
            for reading in getDataToDelete.fetchall():
                prevId = dbObject.checkEmployeeInfoTableToDelete(reading[0],reading[1],database)
                f.deleteTemplate(prevId)
                dbObject.deleteFromEmployeeInfoTable(reading[0],reading[1],database)
                dbObject.deleteFromTempTableToSync(reading[0],reading[1],database)
                count = count + 1
                print ("Data : ",count, " Deleted : ",reading[0])
                t.sleep(.5)
                                                     

        if (getDataToSync != "Synced"):
            count = 0
            for reading in getDataToSync.fetchall():
                prevId = dbObject.checkEmployeeInfoTableToDelete(reading[2],reading[7],database)
                if prevId > 0:
                    f.deleteTemplate(prevId)
                    dbObject.deleteFromEmployeeInfoTable(reading[2],reading[7],database)
                createNewTemplate(f,reading)
                count = count + 1
                print ("Data  : ",count, " Enrolled : ",reading[2])
                t.sleep(.5)
        else:
            print "Device Is Fully Synced With The Server"
        updateListOfUsedTemplates(f)
    except Exception as e:
        print('Operation failed!')
        print('Exception message: ' + str(e))
        
if __name__ == '__main__':
    f = configureFingerPrint()
    syncWithOtherDevices(f)
    dbObject.databaseClose(database)
    print "Device Is Fully Synced With The Server"
