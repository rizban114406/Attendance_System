import datetime
import time as t
from attendanceLCDPrint import attendanceLCDPrint
from attendanceFileConfig import attendanceFileConfig
lcdPrint = attendanceLCDPrint()
fileObject = attendanceFileConfig()
if __name__ == '__main__':
	while True:
		desiredTask = fileObject.readDesiredTask()
		if desiredTask == "1":
			nowTime = datetime.datetime.now()
	        currentTime = nowTime.strftime('%H:%M:%S')
	        currentDate = nowTime.strftime('%Y-%m-%d')
	        lcdPrint.printTime(currentTime,currentDate)
	        t.sleep(1)
	    else:
	    	t.sleep(1)