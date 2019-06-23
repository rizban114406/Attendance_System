#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PyFingerprint
Copyright (C) 2015 Bastian Raschke <bastian.raschke@posteo.de>
All rights reserved.

"""
from pyfingerprint.pyfingerprint import PyFingerprint
from attendanceDatabaseConfig import attendanceDatabaseConfig
import time as t
from attendanceFileConfig import attendanceFileConfig
dbObject = attendanceDatabaseConfig()
database = dbObject.connectDataBase()
fileObject = attendanceFileConfig()

## Deletes a finger from sensor
##


##Tries to initialize the sensor
try:
    f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)

    if ( f.verifyPassword() == False ):
        raise ValueError('The given fingerprint sensor password is wrong!')
    print('Currently used templates: ' + str(f.getTemplateCount()) +'/'+ str(f.getStorageCapacity()))
    for num in range(0,999):
        f.deleteTemplate(num)
        t.sleep(.1)
    print('Currently used templates: ' + str(f.getTemplateCount()))

except Exception as e:
    print('The fingerprint sensor could not be initialized!')
    print('Exception message: ' + str(e))

##Tries to delete the template of the finger
try:
    dbObject.createTableEmployeeInfoTable(database)
    dbObject.createTableEventListTable(database)
    dbObject.createTableEmployeeCardInfo(database)
    dbObject.createTableCompanyListTable(database)
    dbObject.createTableTempTableToSync(database)
    dbObject.createTableDeviceInfoTable(database)
    fileObject.updateConfigUpdateStatus('0')
    dbObject.databaseClose(database)
    print ("Device Initialized")
except Exception as e:
    dbObject.createTableEmployeeInfoTable(database)
    dbObject.createTableEventListTable(database)
    dbObject.createTableEmployeeCardInfo(database)
    dbObject.createTableCompanyListTable(database)
    dbObject.createTableTempTableToSync(database)
    dbObject.createTableDeviceInfoTable(database)
    fileObject.updateConfigUpdateStatus('0')
    dbObject.databaseClose(database)
    print ("Device Initialized")
    exit(1)
