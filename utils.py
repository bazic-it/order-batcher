from config import *
from datetime import datetime
import os

def getTimestamp():
    now = datetime.now()
    return datetime.strftime(now, "%m%d%Y%H%M%S")

def getCurrentime():
    return datetime.now()

def getFileModifiedDate(filepath):
    return datetime.fromtimestamp(os.path.getmtime(filepath))

def getDaysDifferent(currentTime, timestamp):
    return (currentTime - timestamp).days

def roundCurrency(cur):
    return round(cur, 4)

def validateInputFilename(filename):
    cleaned = filename
    if '/' in filename:
        cleaned = filename.split('/')[-1]

    if '.csv' not in cleaned:
        cleaned = cleaned + '.csv'

    return USER_DOWNLOADS + cleaned

def getUOMMasterFilepath():
    return os.path.join(ASSETS_BASE_DIR, UOM_MASTER_FILENAME)

def getInventoryMasterFilepath():
    return os.path.join(ASSETS_BASE_DIR, INVENTORY_MASTER_FILENAME)

def writeLog(timestamp, status):
    path = os.path.join(ASSETS_BASE_DIR, LOGS_FILENAME)
    user = os.getenv('COMPUTERNAME')

    items = status["notExistSKUs"] or status["outOfStockSKUs"]

    try:
        with open(path, 'a') as file:
            file.write('USR;{} | IN;{} | SUCCESS;{} | ERR;{} | WARNING;{} | WARN;{} | ITEMS;{} | OUT;{} | VER;{} | TS;{}\n'.format(user, status["inputFilename"], status["success"], status["errorMessage"], status["warning"], status["warningMessage"], items, status["outputFilename"], APP_VERSION, timestamp))
    except:
        print('*** Error: Failed to write to logs. ***')