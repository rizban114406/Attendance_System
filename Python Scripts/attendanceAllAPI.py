import json
import requests
from attendanceFileConfig import attendanceFileConfig
from attendanceDatabaseConfig import attendanceDatabaseConfig
fileObject = attendanceFileConfig()
class attendanceAllAPI:
    dbObject = attendanceDatabaseConfig()
    database = dbObject.connectDataBase()
    ipAddress = ""
    baseURL = ""
    mainURL = ""
    
    def __init__(self):
        print "API FIles"
        desiredDetails = self.dbObject.getAllConfigurationDetails(self.database)
        self.ipAddress = desiredDetails[1]
        self.baseURL = desiredDetails[2]
        self.mainURL = "http://" + self.ipAddress + self.baseURL
        self.dbObject.databaseClose(self.database)

    def checkServerStatus(self,employeeId,selectedCompany):
        try:
            mainURL = self.mainURL + "valid_employee.php"
            payload = {"employee"  : employeeId, \
                       "companyId" : selectedCompany}
            r = requests.post(mainURL, data = payload, timeout = 40)
            print r.content
            output = json.loads(r.content)
            if (output['status'] == 'success' and output['code'] == "1"):
                return str(output['data'])
            elif(output['status'] == 'failed' and output['code'] == "2"):
                return "Registered"
            elif(output['status'] == 'failed' and output['code'] == "0"):
                return "Invalid"    
        except Exception,e:
            print str(e)
            fileObject.updateExceptionMessage("attendanceAllAPI{checkServerStatus}",str(e))
            return "Server Down"

    def getFingerId(self,uniqueId,matrix,selectedCompany,deviceId):
        try:
            receivedData = []
            mainURL = self.mainURL + "fingerprint_enrollment.php"
            payload = {"uniqueId"     : uniqueId, \
                       "fingerMatrix" : matrix , \
                       "deviceId"     : deviceId, \
                       "companyId"    : selectedCompany}
            r = requests.post(mainURL, data = payload, timeout = 40)
            print r.content
            output = json.loads(r.content)
            if (output['status'] == 'success'):
                receivedData.append(output['data']['employeeid'])
                receivedData.append(output['data']['uniqueid'])
                receivedData.append(output['data']['firstname'])
                receivedData.append(output['data']['fingernumber'])
                return receivedData
            else:
                return "No"
        except Exception,e:
            print str(e)
            fileObject.updateExceptionMessage("attendanceAllAPI{getFingerId}",str(e))
            return "Server Error"

    def sendEventData(self,mainData):
        try:
            mainURL = self.mainURL + "device_data.php"
            dataToSend = json.dumps(mainData,sort_keys = True)
#            print(dataToSend)
            payload = {"data" : dataToSend}
            r = requests.post(mainURL, data = payload,timeout = 40)
            print r.content
            output = json.loads(r.content)
            if (output['status'] == 'success'):
                return "Success"
            else:
                return "Not Successfull"
        except Exception as e:
            fileObject.updateExceptionMessage("attendanceAllAPI{sendEventData}",str(e))
            return str(e)

    def getDataToSync(self,receivedData,deviceId):
        try:
            mainURL = self.mainURL + "fingerprint_sync.php"
            dataToSend = json.dumps(receivedData)
##            print dataToSend
##            print deviceId
            payload = {"data" : dataToSend}
            r = requests.post(mainURL, data = payload,timeout = 200)
            print r.content
            output = json.loads(r.content)
            if (output['status'] == 'success'):
                return output['data']
            else:
                return "Some Thing Is Wrong"       
        except Exception as e:
            print str(e)
            fileObject.updateExceptionMessage("attendanceAllAPI{getDataToSync}",str(e))
            return "Server Error"

    def getCardDataToSync(self,receivedData,deviceId):
        try:
            mainURL = self.mainURL + "rfid_sync.php"
#            print mainURL
            dataToSend = json.dumps(receivedData)
            print dataToSend
##            print deviceId
            payload = {"data"      : dataToSend,\
                       "deviceId" : deviceId}
            r = requests.post(mainURL, data = payload,timeout = 200)
            print r.content
            output = json.loads(r.content)
#           print output
            if (output['status'] == 'success'):
                if output['data']['sync_status'] == '0':
                    fileObject.updateConfigUpdateStatus('0')
                return output['data']
            else:
                return "Some Thing Is Wrong"
        
        except Exception as e:
            print str(e)
            fileObject.updateExceptionMessage("attendanceAllAPI{getCardDataToSync}",str(e))
            return "Server Error"

    def authenticatePassword(self,password,deviceId):
        try:
            mainURL = self.mainURL + "check_device_auth.php"
            payload = {"deviceId" : deviceId, \
                       "password"  : password }
            
            r = requests.post(mainURL, data = payload,timeout = 10)
            print r.content
            output = json.loads(r.content)
            if (output['status'] == "success"):
                return "Matched"
            else:
                return "Not Matched"
        
        except Exception as e:
            #print str(e)
            fileObject.updateExceptionMessage("attendanceAllAPI{authenticatePassword}",str(e))
            return "Server Error"

    def updateDevice(self,deviceId,ipAddress,osVersion,sync_status):
        try:
            mainURL = self.mainURL + "update_device.php"
            payload = {"deviceId"  : deviceId,   \
                       "ip"        : ipAddress, \
                       "osversion" : osVersion,  \
                       "syncstatus": sync_status }
            r = requests.post(mainURL, data = payload,timeout = 10)
            print r.content
            output = json.loads(r.content)
            #print r.content
            if (output['status'] == "success" and output['code'] == "1"):
                return '1'
            else:
                return '0'
        
        except Exception as e:
            print str(e)
            fileObject.updateExceptionMessage("attendanceAllAPI{updateDevice}",str(e))
            return "Server Error"

    def getDeviceInfo(self,deviceId):
        try:
            mainURL = self.mainURL + "get_device.php"
            payload = {"deviceId" : deviceId }
            r = requests.post(mainURL, data = payload,timeout = 10)
            print r.content
            output = json.loads(r.content)
            if (output['status'] == "success" and output['code'] == "1"):
                return output['data']
            else:
                return '0'
        
        except Exception as e:
            print str(e)
            fileObject.updateExceptionMessage("attendanceAllAPI{getDeviceInfo}",str(e))
            return "Server Error"

    def getCompanyDetails(self,deviceId):
        try:
            mainURL = self.mainURL + "get_company.php"
            payload = {"deviceId" : deviceId }
            r = requests.post(mainURL, data = payload,timeout = 10)
            print r.content
            output = json.loads(r.content)
            if (output['status'] == "success"):
                return output['data']
            else:
                return '0'
        
        except Exception as e:
            print str(e)
            fileObject.updateExceptionMessage("attendanceAllAPI{getCompanyDetails}",str(e))
            return "Server Error"

    def createDevice(self,hardwareId,osVersion):
        try:
            mainURL = self.mainURL + "create_device.php"
            payload = {"hardwareId" : hardwareId, \
                       "osVersion"  : osVersion }
            print payload
            r = requests.post(mainURL, data = payload,timeout = 10)
            print r.content
            output = json.loads(r.content)
            if (output['status'] == "success" and output['code'] == "1"):
                return output['data']
            else:
                return '0'
        
        except Exception as e:
            print str(e)
            fileObject.updateExceptionMessage("attendanceAllAPI{createDevice}",str(e))
            return "Server Error"

    def getConfigDetails(self,deviceId):
        try:
            mainURL = self.mainURL + "get_config.php"
            payload = {"deviceId" : deviceId }
            r = requests.post(mainURL, data = payload,timeout = 10)
            output = json.loads(r.content)
            print r.content
            if (output['status'] == "success" and output['code'] == "1"):
                return output['data']
            else:
                return '0'
        
        except Exception as e:
            print str(e)
            fileObject.updateExceptionMessage("attendanceAllAPI{getConfigDetails}",str(e))
            return "Server Error"

        
                

