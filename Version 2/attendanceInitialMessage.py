import datetime
import time as t
from attendanceLCDPrint import attendanceLCDPrint
from attendanceFileConfig import attendanceFileConfig
lcdPrint = attendanceLCDPrint()
fileObject = attendanceFileConfig()
if __name__ == '__main__':
	while True:
		while (fileObject.readDesiredTask() == '1'):
			lcdPrint.printInitialMessage()
			t.sleep(1)
		while (fileObject.readDesiredTask() != '1'):
			t.sleep(1)
