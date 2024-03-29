import datetime
class attendanceFileConfig:

    def readDesiredTask(self):
        file = open('catTask.txt','r')
        desiredTask = file.read(1)
        file.close()
        return desiredTask

    def updateCatTask(self,command):
        file = open('catTask.txt', 'w')
        file.write(command)
        file.close()

    def updateExceptionMessage(self,exceptionScript,exceptionMessage):
        nowTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message = "Exception From :"     + exceptionScript  + \
                  " Exception Message: " + exceptionMessage + \
                  " Time: "              + str(nowTime)     + "\n"
        file = open('exceptionMessage.txt', 'a+')
        file.write(message)
        file.close()

    def updateConfigUpdateStatus(self,status):
        file = open('configUpdateStatus.txt', 'w+')
        file.write(status)
        file.close()

    def readConfigUpdateStatus(self):
        try:
            file = open('configUpdateStatus.txt','r')
            configStatus = file.read(1)
            file.close()
            return configStatus
        except Exception as e:
            self.updateConfigUpdateStatus('0')
            return '0'

    def readStoredIndex(self):
        try:           
            file = open('storedIndex.txt','r')
            template = file.readline()
            storedTemplate = template.split('-')
            file.close()
        except Exception, e:
            storedTemplate = []
            self.updateStoredIndex("")
        return storedTemplate

    def updateStoredIndex(self,storedIndex):
        file = open('storedIndex.txt', 'w+')
        file.write(storedIndex)
        file.close()

    def updateHearBitURL(self,url):
        file = open('heartBitUrl.txt', 'w+')
        file.write(url)
        file.close()
        
