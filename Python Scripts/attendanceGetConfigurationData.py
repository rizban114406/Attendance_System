import urllib
import tarfile
from shutil import copyfile
import os
import struct
from attendanceDatabaseConfig import attendanceDatabaseConfig
from attendanceAllAPI import attendanceAllAPI
from attendanceFileConfig import attendanceFileConfig
fileObject = attendanceFileConfig()
import commands
import time as t

def myCommands():
    try:
        try:
            os.system('sudo rm /var/lib/mysql/ibdata1')
        except Exception,e:
            print str(e)
        try:
            os.system('sudo rm /var/lib/mysql/AttendanceSystem/*')
        except Exception,e:
            print str(e)
        try:
            os.system('sudo rm /var/lib/mysql/ib_logfile*')
        except Exception,e:
            print str(e)
        os.system('sudo python initializeDatabase.py')
    except Exception,e:
        fileObject.updateExceptionMessage("attendanceGetConfigurationData{myCommands}",str(e))
try:
    dbObject = attendanceDatabaseConfig()
    database = dbObject.connectDataBase()
except Exception,e:
    fileObject.updateExceptionMessage("attendanceGetConfigurationData{DB Error}",str(e))
    myCommands()
    dbObject = attendanceDatabaseConfig()
    database = dbObject.connectDataBase()

apiObject = attendanceAllAPI()

def getHardwareId():
    # Extract serial from cpuinfo file
    cpuserial = "0000000000000000"
    try:
        f = open('/proc/cpuinfo','r')
        for line in f:
            # print line[0:4]
            if line[0:6]=='Serial':
                cpuserial = line[10:26]
        f.close()
    except Exception, e:
        print "ex1"
        print str(e)
        cpuserial = "Error"
    return cpuserial

def getIpAddress():
    ip =  commands.getoutput('hostname -I')
    #ip = "10.203.96.23"
    return ip

##def getSubnetAddress():
##    ip =  commands.getoutput('ifconfig eth0 | awk '/Mask:/{split($4,a,":"); print a[2]}'')
##    #ip = "10.203.96.23"
##    return ip

def updateToNewCode(deviceCodeName,deviceCodeURL,baseURL):
    
    downloadURL = "http://" + baseURL + deviceCodeURL + deviceCodeName
    # print downloadURL
    try:
        testfile = urllib.URLopener()     
        testfile.retrieve(downloadURL, deviceCodeName)       
        #Extract Tar File
        try:
            tar = tarfile.open(deviceCodeName)
            tar.extractall()
            tar.close()
        except struct.error, e:  # or except struct.error as e, depends on Python version
            print "Corrupt:"
        except tarfile.TarError, e:
            print "Tar error: (%s)" % (str(e))
        
        if os.path.exists("/root/rc.local"):
            copyfile("/root/rc.local", "/etc/rc.local")
        os.system('chmod 755 *')
        return 1
    except Exception, e:
        fileObject.updateExceptionMessage("attendanceGetConfigurationData{updateToNewCode}",str(e))
        return 0

def restart():
    dbObject.databaseClose(database)
    command = "/usr/bin/sudo /sbin/shutdown -r now"
    import subprocess
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]

def getNetworkConfiguration(deviceId):
    try:
        configDetails = dbObject.getAllConfigurationDetails(database)
        configDetailsUpdated = apiObject.getConfigDetails(deviceId)
        if configDetailsUpdated != '0' and configDetailsUpdated != "Server Error":
            if str(configDetailsUpdated['base_url']) != str(configDetails[1]):
                dbObject.updateBaseUrl(str(configDetailsUpdated['base_url']),database)
            if str(configDetailsUpdated['sub_url']) != str(configDetails[2]):
                dbObject.updateSubUrl(str(configDetailsUpdated['sub_url']),database)
            if float(configDetailsUpdated['device_os_version']) > float(configDetails[0]):
                codeUpdateFlag = updateToNewCode(str(configDetailsUpdated['device_code_name']),\
                                                 str(configDetailsUpdated['device_code_url']),\
                                                 str(configDetailsUpdated['base_url']))
                if codeUpdateFlag == 1:
                    dbObject.updateOSVersion(float(configDetailsUpdated['device_os_version']),database)
                    restart()            
            return '1'
        else:
            return configDetailsUpdated
    except Exception as e:
        fileObject.updateExceptionMessage("attendanceGetConfigurationData{getNetworkConfiguration}",str(e))
        return configDetailsUpdated

def getCompanyDetails(deviceId):
    try:
        allCompanies = apiObject.getCompanyDetails(deviceId)
        #print allCompanies
        if allCompanies != '0' and allCompanies != "Server Error":
            dbObject.createTableCompanyListTable(database)
            for company in allCompanies:
                dbObject.insertIntoCompanyListTable(company['CompanyId'],company['ShortName'],database)
            return '1'
        else:
            return '0'
    except Exception as e:
        fileObject.updateExceptionMessage("attendanceGetConfigurationData{getCompanyDetails}",str(e))
        return '0'
    
def sendConfirmationToServer(deviceId,ipAddress):
    osVersion = dbObject.getOSVersion(database)
    updateStatus = apiObject.updateDevice(deviceId,ipAddress,osVersion,'1')
    if updateStatus == '1':
        #print "Updating Flag"
        fileObject.updateConfigUpdateStatus('1')
        return '1'
    else:
        return '0'

def updateHeartBitURL():
    configDetails = dbObject.getAllConfigurationDetails(database)
    url = "http://" + configDetails[1] + configDetails[2] + "server_heartbit"
    fileObject.updateHearBitURL(url)

def checkIPAddress(deviceId,ipAddress):
    desiredDetails = dbObject.getAllDeviceInfo(database)
    if (ipAddress != desiredDetails[6]):
        status = sendConfirmationToServer(deviceId,ipAddress)
        if status == '1':
            dbObject.updateIPAddress(ipAddress,database)

if __name__ == '__main__':
    try:
        deviceId = dbObject.getDeviceId(database)
        hardwareId = getHardwareId()
        osVersion = dbObject.getOSVersion(database)
        ipAddress = getIpAddress()
        if deviceId == 0:
            #print "No Device ID"
            deviceInfo = apiObject.createDevice(hardwareId,osVersion)
            if (deviceInfo != '0' and deviceInfo != "Server Error"):
                dbObject.insertIntoDeviceInfoTable(deviceInfo,ipAddress,database)
                deviceId = int(deviceInfo['id'])
                
            if deviceId != 0:
                networkConfigStatus = getNetworkConfiguration(deviceId)
                companyListStatus = getCompanyDetails(deviceId)
                if networkConfigStatus == '1' and companyListStatus == '1':
                    updateHeartBitURL()
                    sendConfirmationToServer(deviceId,ipAddress)
        else:
            readUpdateStatus = fileObject.readConfigUpdateStatus()
            #print readUpdateStatus
            if readUpdateStatus == '0':
                deviceInfo = apiObject.getDeviceInfo(deviceId)
                if (deviceInfo != '0' and deviceInfo != "Server Error"):
                    dbObject.updateDeviceInfoTable(deviceInfo,ipAddress,database)
                    networkConfigStatus = getNetworkConfiguration(deviceId)
                    companyListStatus = getCompanyDetails(deviceId)
                    if networkConfigStatus == '1' and companyListStatus == '1':
                        updateHeartBitURL()
                        sendConfirmationToServer(deviceId,ipAddress)
            else:
                checkIPAddress(deviceId,ipAddress)
        dbObject.databaseClose(database)
    
    except Exception as e:
        dbObject.databaseClose(database)
        fileObject.updateExceptionMessage("attendanceGetConfigurationData{__main__}",str(e))

    

    
        
        
