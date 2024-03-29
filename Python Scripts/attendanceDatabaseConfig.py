import MySQLdb
from attendanceFileConfig import attendanceFileConfig
import time as t
fileObject = attendanceFileConfig()
class attendanceDatabaseConfig:
    address = "localhost"
    user = "attendanceUser"
    password = "password"
    database = "AttendanceSystem"

##    def __init__(self):
##        print "DaTa Base Configuration File"

    def databaseCommit(self,database):
        database.commit()

    def databaseClose(self,database):
        database.close()

    def connectDataBase(self):
        database = MySQLdb.connect(self.address, self.user, self.password, self.database,charset='utf8')
        return database

    ####################### All Functions Regarding Employee Information Table ###################
    def createTableEmployeeInfoTable(self,database): # Create Employee Information Table
        curs = database.cursor()
        try:      
            curs.execute("DROP TABLE employeeInfoTable")
            self.databaseCommit(database)
            t.sleep(1)
        except Exception:
            print "Does not Exists"
        curs.execute("CREATE TABLE employeeInfoTable(id INT NOT NULL AUTO_INCREMENT,\
                                                     employeeId varchar(50),\
                                                     uniqueId INT,\
                                                     firstName varchar(200),\
                                                     fingerId INT, \
                                                     fingerMatrix TEXT, \
                                                     companyId INT, \
                                                     employee varchar(50),\
                                                     PRIMARY KEY(id))")
        self.databaseCommit(database)

    def deleteFromEmployeeInfoTable(self,uniqueId,companyId,database): # Delete From Employee Infromation Table After Deleting Employee
        curs = database.cursor()
        curs.execute("Delete FROM employeeInfoTable \
                      WHERE uniqueId = %s and companyId = %s",(int(uniqueId),int(companyId)))
        self.databaseCommit(database)

    def deleteFromEmployeeInfoTableToSync(self,notListedTemplateNumber,database): # Delete From Employee Infromation Table After Deleting Employee
        curs = database.cursor()
        for fingerId in notListedTemplateNumber:
            curs.execute("Delete FROM employeeInfoTable \
                          WHERE fingerId = %s",(int(fingerId)))
        self.databaseCommit(database)

    def truncateEmployeeInfoTable(self,database): # Delete From Employee Infromation Table After Deleting Employee
        curs = database.cursor()
        curs.execute("truncate employeeInfoTable")
        self.databaseCommit(database)

    def getInfoFromEmployeeInfoTable(self,database): # Get Data From Employee Info Table To Send It To The Server
        try:
            curs = database.cursor()
            curs.execute("SELECT uniqueId,fingerId,companyId From employeeInfoTable")
            receivedData = []
            #mainData = {"data":receivedData}
            for reading in curs.fetchall():
                receivedData.append({"uniqueid"     : reading[0], \
                                     "fingernumber" : reading[1], \
                                     "companyid"    : reading[2]})
            if (curs.rowcount == 0):
                receivedData.append({"uniqueid"     : 0, \
                                     "fingernumber" : 0, \
                                     "companyid"    : 0})
        except Excecption as e:
            fileObject.updateExceptionMessage("attendanceDatabaseConfig{getInfoFromEmployeeInfoTable}",str(e))
        print receivedData
        return receivedData

    def dropEmployeeInfoTable(self,database): # Drop Employee Information Table
        curs = database.cursor()
        curs.execute("Drop Table employeeInfoTable")
        self.databaseCommit(database)

    def countEmployeeInfoTable(self,database): # Drop Employee Information Table
        curs = database.cursor()
        curs.execute("Select cout(*) from employeeInfoTable")
        employeeNumber = curs.fetchone()
        return int(employeeNumber[0])

    def checkEmployeeInfoTableToDelete(self,uniqueId,companyId,database): # 
        curs = database.cursor()
        curs.execute ("SELECT fingerId \
                       FROM employeeInfoTable \
                       WHERE uniqueId = %s and companyId = %s", \
                      (int(uniqueId),int(companyId)))
        if (curs.rowcount != 0):
            employeeFingerId = curs.fetchone()
            return int(employeeFingerId[0])
        else:
            return 0

    def checkEmployeeInfoTable(self,employee,companyId,database): # 
        curs = database.cursor()
        curs.execute ("SELECT fingerId \
                       FROM employeeInfoTable \
                       WHERE employee = %s and companyId = %s", \
                      (str(employee),int(companyId)))
        if (curs.rowcount != 0):
            return "Registered"
        else:
            return "Not Registered"

    def insertNewEmployee(self,employeeId,\
                          uniqueId,\
                          firstName,\
                          fingerId,\
                          fingerMatrix,\
                          companyId,\
                          employee,\
                          database):
        curs = database.cursor()
        if (firstName is None):
            firstName = ""
        try:
            curs.execute("INSERT INTO employeeInfoTable(employeeId,\
                                                        uniqueId,\
                                                        firstName,\
                                                        fingerId,\
                                                        fingerMatrix,\
                                                        companyId,\
                                                        employee) VALUES (%s,%s,%s,%s,%s,%s,%s)",\
                                                        (str(employeeId),\
                                                        int(uniqueId),\
                                                        str(firstName),\
                                                        int(fingerId),\
                                                        str(fingerMatrix),\
                                                        int(companyId),\
                                                        str(employee)))
            self.databaseCommit(database)
        except Exception as e:
            fileObject.updateExceptionMessage("attendanceDatabaseConfig{insertNewEmployee}",str(e))
            
    def getEmployeeTemplateNumber(self,database):
        curs = database.cursor()
        curs.execute ("SELECT fingerId \
                       FROM employeeInfoTable \
                       ORDER BY fingerId")
        storedTemplates = []
        if (curs.rowcount != 0):
            for reading in curs.fetchall():
                storedTemplates.append(str(reading[0]))

        return storedTemplates
        
    def getEmployeeDetails(self,positionNumber,database):
        curs = database.cursor()
        curs.execute ("SELECT employeeId,uniqueId,firstName,companyId \
                       FROM employeeInfoTable \
                       WHERE fingerId = %s",(positionNumber))
        if (curs.rowcount != 0):
            desiredDetails = curs.fetchone()
            return desiredDetails
        else:
            return '0'
    ####################### All Functions Regarding Employee Information Table ###################

    ############################# All Functions Regarding Temporary Table ########################
    def createTableTempTableToSync(self,database): # Create A Temporary Table To Sync With The Server
        curs = database.cursor()
        try:      
            curs.execute("Drop Table tempTableToSync")
            self.databaseCommit(database)
            t.sleep(1)
        except Exception:
            print "Does not Exists"
        curs.execute("CREATE TABLE tempTableToSync(id INT NOT NULL AUTO_INCREMENT,\
                                                   employeeId varchar(50),\
                                                   uniqueId INT,\
                                                   firstName varchar(200),\
                                                   fingerId INT, \
                                                   fingerMatrix TEXT, \
                                                   desiredTask varchar(2), \
                                                   companyId INT, \
                                                   PRIMARY KEY(id))")
        self.databaseCommit(database)

    def truncateTempTableToSync(self,database): # Delete From Employee Infromation Table After Deleting Employee
        curs = database.cursor()
        curs.execute("truncate tempTableToSync")
        self.databaseCommit(database)

    def insertToTempTableToSync(self,employeeId,\
                                uniqueId,\
                                firstName,\
                                fingerId,\
                                fingerMatrix,\
                                desiredTask,\
                                companyId, \
                                database): # Insert Into Temporary Table To Sync With The Server
        curs = database.cursor()
        if (firstName is None):
            firstName = ""
        try:
            curs.execute("INSERT INTO tempTableToSync(employeeId,\
                                                      uniqueId,\
                                                      firstName,\
                                                      fingerId,\
                                                      fingerMatrix,\
                                                      desiredTask,\
                                                      companyId) VALUES (%s,%s,%s,%s,%s,%s,%s)",\
                                                      (str(employeeId),\
                                                      int(uniqueId),\
                                                      str(firstName),\
                                                      int(fingerId),\
                                                      str(fingerMatrix),\
                                                      str(desiredTask),\
                                                      int(companyId)))
            self.databaseCommit(database)
        except Exception as e:
            fileObject.updateExceptionMessage("attendanceDatabaseConfig{insertToTempTableToSync}",str(e))

    def deleteFromTempTableToSync(self,uniqueId,companyId,database): # Delete From Temporary Table After Synced
        curs = database.cursor()
        curs.execute("Delete FROM tempTableToSync \
                      WHERE uniqueId = %s and companyId = %s",(int(uniqueId),int(companyId)))
        self.databaseCommit(database)

    def getInfoFromTempTableToDelete(self,database): # Get Data From Temporary Table To Sync With The Server
        curs = database.cursor()
        try:     
            curs.execute("SELECT uniqueId,companyId From tempTableToSync Where desiredTask = '3'")
            if (curs.rowcount != 0):
                return curs
            else:
                return "Synced"
        except Exception as e:
            fileObject.updateExceptionMessage("attendanceDatabaseConfig{getInfoFromTempTableToDelete}",str(e))
            return "Synced"

    def getInfoFromTempTableToEnrollOrUpdate(self,database): # Get Data From Temporary Table To Sync With The Server
        curs = database.cursor()
        try:        
            curs.execute("SELECT * From tempTableToSync Where desiredTask = '1' Limit 200")
            if (curs.rowcount != 0):
                return curs
            else:
                return "Synced"
        except Exception as e:
            fileObject.updateExceptionMessage("attendanceDatabaseConfig{getInfoFromTempTableToEnrollOrUpdate}",str(e))
            return "Synced"
    ############################# All Functions Regarding Temporary Table ########################

    ######################### All Functions Regarding Event Information Table ####################
    def createTableEventListTable(self,database):
        curs = database.cursor()
        try:      
            curs.execute("DROP TABLE eventListTable")
            self.databaseCommit(database)
            t.sleep(1)
        except Exception:
            print "Does not Exists"
        curs.execute("CREATE TABLE eventListTable(id INT NOT NULL AUTO_INCREMENT,\
                                                 uniqueId INT,\
                                                 fingerOrCard INT,\
                                                 eventDateTime datetime,\
                                                 eventType varchar(1),\
                                                 companyId INT, \
                                                 PRIMARY KEY(id))")
        self.databaseCommit(database)

    def truncateEventListTable(self,database): # Delete From Employee Infromation Table After Deleting Employee
        curs = database.cursor()
        curs.execute("truncate eventListTable")
        self.databaseCommit(database)
        
    def deleteFromEventListTable(self,Id,database):
        curs = database.cursor()
        curs.execute("Delete FROM eventListTable WHERE id = %s",(Id))
        self.databaseCommit(database)

    def getAllEventData(self,database):
        curs = database.cursor()
        curs.execute("SELECT * From eventListTable Limit 1000")
        self.databaseCommit(database)
        return curs

    def insertEventTime(self,uniqueId,\
                        fingerOrCard,\
                        EventDateTime,\
                        EventType,\
                        companyId,\
                        database):
        curs = database.cursor()
        curs.execute("INSERT INTO eventListTable(uniqueId,\
                                                 fingerOrCard,\
                                                 EventDateTime,\
                                                 EventType,\
                                                 companyID) VALUES (%s,%s,%s,%s,%s)",\
                                                (int(uniqueId),\
                                                 int(fingerOrCard),\
                                                 EventDateTime,\
                                                 EventType,\
                                                 int(companyId)))
        self.databaseCommit(database)
    ######################### All Functions Regarding Event Information Table ####################

    ####################### All Functions Regarding Employee Card Info ###################
    def createTableEmployeeCardInfo(self,database): # Create Employee Card Info Table
        curs = database.cursor()
        try:      
            curs.execute("DROP TABLE employeeCardInfo")
            self.databaseCommit(database)
            t.sleep(1)
        except Exception:
            print "Does not Exists"
        curs.execute("CREATE TABLE employeeCardInfo(id INT NOT NULL AUTO_INCREMENT,\
                                                   employeeId varchar(50),\
                                                   uniqueId INT,\
                                                   firstName varchar(200),\
                                                   cardNumber INT, \
                                                   companyId INT, \
                                                   PRIMARY KEY(id))")
        self.databaseCommit(database)

    def deleteFromEmployeeCardInfoTable(self,uniqueId,cardNumber,database): # Delete From Employee Card Info Table After Deleting Employee
        curs = database.cursor()
        if (cardNumber == 0):
            curs.execute("Delete FROM employeeCardInfo \
                          WHERE uniqueId = %s",(int(uniqueId)))
        else:
            curs.execute("Delete FROM employeeCardInfo \
                          WHERE uniqueId = %s and cardNumber = %s", \
                         (int(uniqueId),int(cardNumber)))
            
        self.databaseCommit(database)

    def truncateEmployeeCardInfoTable(self,database): # Delete From Employee Card Info Table After Deleting Employee
        curs = database.cursor()
        curs.execute("truncate employeeCardInfo")
        self.databaseCommit(database)

    def getInfoFromEmployeeCardInfoTable(self,database): # Get Data From Employee Card Info Table To Send It To The Server
        curs = database.cursor()
        curs.execute("Select uniqueId , cardNumber \
                      From employeeCardInfo")
        receivedData = []
        for reading in curs.fetchall():
            receivedData.append({"uniqueid" : reading[0], "cardNumber" : reading[1]})
        if (curs.rowcount == 0):
            receivedData.append({"uniqueid" : 0, "cardNumber" : 0})
        return receivedData

    def dropEmployeeCardInfoTable(self,database): # Drop Employee Card Info Table
        curs = database.cursor()
        curs.execute("Drop Table employeeCardInfo")
        self.databaseCommit(database)

    def checkEmployeeCardInfoTableToDelete(self,uniqueId,companyId,database): # 
        curs = database.cursor()
        try:
            curs.execute ("SELECT cardNumber \
                           FROM employeeCardInfo \
                           WHERE uniqueId = %s and companyId = %s",(int(uniqueId),int(companyId)))
            if (curs.rowcount != 0):
                self.deleteFromEmployeeCardInfoTable(uniqueId,0,database)
                self.databaseCommit(database)
            return 1
        except Exception as e:
            #print str(e)
            fileObject.updateExceptionMessage("attendanceDatabaseConfig{checkEmployeeCardInfoTableToDelete}",str(e))
            return 0

    def insertIntoEmployeeCardInfoTable(self,employeeId,\
                                        uniqueId,\
                                        firstName,\
                                        cardNumber,\
                                        companyId,\
                                        database):
        curs = database.cursor()
        if (firstName is None):
            firstName = ""
        try:
            curs.execute("INSERT INTO employeeCardInfo(employeeId,\
                                                       uniqueId,\
                                                       firstName,\
                                                       cardNumber,\
                                                       companyId) VALUES (%s,%s,%s,%s,%s)",\
                                                       (str(employeeId),\
                                                       int(uniqueId),\
                                                       str(firstName),\
                                                       int(cardNumber),\
                                                       int(companyId)))
            self.databaseCommit(database)
        except Exception as e:
            print str(e)
            fileObject.updateExceptionMessage("attendanceDatabaseConfig{insertIntoEmployeeCardInfoTable}",str(e))

    def getEmployeeDetailsFromCard(self,cardNumber,database):
        curs = database.cursor()
        curs.execute ("SELECT employeeId,uniqueId,firstName,companyId \
                       FROM employeeCardInfo \
                       WHERE cardNumber = %s",(int(cardNumber)))
        self.databaseCommit(database)
        if (curs.rowcount != 0):
            desiredDetails = curs.fetchone()
            return desiredDetails
        else:
            return '0'
    ####################### All Functions Regarding Employee Card Info Table ###################

    ####################### All Functions Regarding Company Info Table ###################
    def createTableCompanyListTable(self,database):
        curs = database.cursor()
        try:      
            curs.execute("DROP TABLE companyListTable")
            self.databaseCommit(database)
            t.sleep(1)
        except Exception:
            print "Does not Exists"
        curs.execute("CREATE TABLE companyListTable(id INT NOT NULL AUTO_INCREMENT,\
                                                  companyId INT,\
                                                  shortName text,\
                                                  PRIMARY KEY(id))")
        self.databaseCommit(database)

    def getAllCompanyList(self,database):
        curs = database.cursor()
        curs.execute("Select companyId,shortName From companyListTable")
        self.databaseCommit(database)
        return curs

    def checkCompanyListTable(self,companyId,database): 
        curs = database.cursor()
        curs.execute ("SELECT companyName FROM companyListTable WHERE companyId = %s",(int(companyId)))
        if (curs.rowcount != 0):
            return '1'
        else:
            return '0'

    def insertIntoCompanyListTable(self,companyId,\
                                        shortName,\
                                        database):
        curs = database.cursor()
        curs.execute("INSERT INTO companyListTable(companyId,\
                                                   shortName) VALUES (%s,%s)",\
                                                   (int(companyId),\
                                                   str(shortName)))
        self.databaseCommit(database)
    ####################### All Functions Regarding Company Info Table ###################

    ####################### All Functions Regarding Configuration Info Table ###################

    def createTableConfigInfoTable(self,database):
        curs = database.cursor()
        try:      
            curs.execute("DROP TABLE configurationTable")
            self.databaseCommit(database)
        except Exception:
            print "Does not Exists"
        curs.execute("CREATE TABLE configurationTable(id INT NOT NULL AUTO_INCREMENT,\
                                                  deviceOSVersion double,\
                                                  baseUrl text,\
                                                  subUrl text,\
                                                  PRIMARY KEY(id))")
        self.databaseCommit(database)
        
    def getAllConfigurationDetails(self,database):
        curs = database.cursor()
        curs.execute ("SELECT deviceOSVersion,baseUrl,subUrl FROM configurationTable WHERE id = 1")
        if (curs.rowcount != 0):
            desiredDetails = curs.fetchone()
            return desiredDetails
        else:
            return '0'
    def getOSVersion(self,database):
        curs = database.cursor()
        curs.execute ("SELECT deviceOSVersion FROM configurationTable WHERE id = 1")
        if (curs.rowcount != 0):
            desiredDetails = curs.fetchone()
            return float(desiredDetails[0])
        else:
            return '0'

    def insertIntoConfigurationTable(self,deviceOSVersion,\
                                        baseUrl,\
                                        subUrl,\
                                        database):
        curs = database.cursor()
        curs.execute("INSERT INTO configurationTable(deviceOSVersion,\
                                                   baseUrl,\
                                                   subUrl) VALUES (%s,%s,%s)",\
                                                   (str(deviceOSVersion),\
                                                    str(baseUrl),\
                                                    str(subUrl)))
        self.databaseCommit(database)

    def updateOSVersion(self,deviceOSVersion,database):
        curs = database.cursor()
        curs.execute ("UPDATE configurationTable SET deviceOSVersion = %s \
                                                     WHERE id = 1",\
                                                    (deviceOSVersion))
        self.databaseCommit(database)
    def updateBaseUrl(self,baseUrl,database):
        curs = database.cursor()
        curs.execute ("UPDATE configurationTable SET baseUrl = %s \
                                                     WHERE id = 1",\
                                                    (baseUrl))
        self.databaseCommit(database)
    def updateSubUrl(self,subUrl,database):
        curs = database.cursor()
        curs.execute ("UPDATE configurationTable SET subUrl = %s \
                                                     WHERE id = 1",\
                                                    (subUrl))
        self.databaseCommit(database)
    
    ####################### All Functions Regarding Configuration Info Table ###################

    ####################### All Functions Regarding Device Info Table ###################

    def createTableDeviceInfoTable(self,database):
        curs = database.cursor()
        try:      
            curs.execute("DROP TABLE deviceInfoTable")
            self.databaseCommit(database)
            t.sleep(1)
        except Exception:
            print "Does not Exists"
        curs.execute("CREATE TABLE deviceInfoTable(id INT NOT NULL AUTO_INCREMENT,\
                                                  deviceId int,\
                                                  hardwareId text,\
                                                  companyId varchar(3),\
                                                  address text,\
                                                  subAddress text,\
                                                  ipAddress text,\
                                                  PRIMARY KEY(id))")
        self.databaseCommit(database)

    def getDeviceId(self,database):
        curs = database.cursor()
        curs.execute ("SELECT deviceId FROM deviceInfoTable WHERE id = 1")
        if (curs.rowcount != 0):
            desiredDetails = curs.fetchone()
            return int(desiredDetails[0])
        else:
            return 0

    def getAllDeviceInfo(self,database):
        curs = database.cursor()
        curs.execute ("SELECT * FROM deviceInfoTable WHERE id = 1")
        if (curs.rowcount != 0):
            desiredDetails = curs.fetchone()
            return desiredDetails
        else:
            return '0'

    def updateIPAddress(self,ipAddress,database):
        curs = database.cursor()
        curs.execute ("UPDATE deviceInfoTable SET ipAddress = %s \
                                                  WHERE id = 1",\
                                                  (ipAddress))
        self.databaseCommit(database)

    def insertIntoDeviceInfoTable(self,deviceInfo,\
                                  ipAddress,\
                                  database):
        curs = database.cursor()
        if (deviceInfo['company_id'] is None):
            deviceInfo['company_id'] = ""
        if (deviceInfo['address'] is None):
            deviceInfo['address'] = ""
        if (deviceInfo['subaddress'] is None):
            deviceInfo['subaddress'] = ""
        try:
            curs.execute("INSERT INTO deviceInfoTable(deviceId,\
                                                      hardwareId,\
                                                      companyId,\
                                                      address,\
                                                      subAddress,\
                                                      ipAddress) VALUES (%s,%s,%s,%s,%s,%s)",\
                                                      (int(deviceInfo['id']),\
                                                       str(deviceInfo['hardware_id']),\
                                                       str(deviceInfo['company_id']),\
                                                       str(deviceInfo['address']),\
                                                       str(deviceInfo['subaddress']),\
                                                       str(ipAddress)))
            self.databaseCommit(database)
        except Exception as e:
            print str(e)
            fileObject.updateExceptionMessage("attendanceDatabaseConfig{insertIntoDeviceInfoTable}",str(e))

    def updateDeviceInfoTable(self,deviceInfo,\
                              ipAddress,\
                              database):
        curs = database.cursor()
        if (deviceInfo['company_id'] is None):
            deviceInfo['company_id'] = ""
        if (deviceInfo['address'] is None):
            deviceInfo['address'] = ""
        if (deviceInfo['subaddress'] is None):
            deviceInfo['subaddress'] = ""
        curs.execute ("UPDATE deviceInfoTable SET companyId = %s, \
                                                  address = %s, \
                                                  subAddress = %s, \
                                                  ipAddress = %s \
                                                  WHERE id = 1",\
                                                  (str(deviceInfo['company_id']),\
                                                   str(deviceInfo['address']),\
                                                   str(deviceInfo['subaddress']),\
                                                   str(ipAddress)))
        self.databaseCommit(database)
        
    ####################### All Functions Regarding Device Info Table ###################
    
