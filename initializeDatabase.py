#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PyFingerprint
Copyright (C) 2015 Bastian Raschke <bastian.raschke@posteo.de>
All rights reserved.

"""

from attendanceDatabaseConfig import attendanceDatabaseConfig
import time as t
from attendanceFileConfig import attendanceFileConfig
dbObject = attendanceDatabaseConfig()
database = dbObject.connectDataBase()
fileObject = attendanceFileConfig()


#### Tries to delete the template of the finger
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
