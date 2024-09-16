# Created: 9/13/2024
# Last updated: 9/16/2024

import os
import sys
import csv
import pandas as pd
from datetime import datetime
from pathlib import Path

APP_VERSION = '1.1'

ASSETS_BASE_DIR = 'S:/ECOM-CC-WHS/master_files'
UOM_MASTER_FILENAME = 'uom_input.csv'
INVENTORY_MASTER_FILENAME = 'warehouse_1_5_input.csv'
USER_DOWNLOADS = str(Path.home() / "Downloads") + '/'

# ASSETS_BASE_DIR = './assets/'
# UOM_MASTER_FILENAME = 'uom_input.csv'
# INVENTORY_MASTER_FILENAME = 'inventory_input.csv'

class Order:
    def __init__(self, sku, itemDescription, itemPrice, orderNumber, orderTotal, paidByCustomer, tax, itemQty, qtyInEach, shipping):
        self.sku = sku
        self.itemDescription = itemDescription
        self.itemPrice = float(itemPrice)
        self.orderNumber = orderNumber
        self.totalSaleOrder = float(itemPrice) * int(itemQty)
        self.orderTotal = float(orderTotal)
        self.paidByCustomer = float(paidByCustomer)
        self.tax = float(tax)
        self.itemQty = int(itemQty)
        self.qtyInEach = int(qtyInEach)
        self.shipping = float(shipping)
    
    def __str__(self):
        return 'sku: {}, itemPrice: {}, qty: {}, qtyInEach: {}'.format(self.sku, self.itemPrice, self.itemQty, self.qtyInEach)

def getTimestamp():
    now = datetime.now()
    return datetime.strftime(now, "%m%d%Y%H%M%S")

def getUOMMasterData(inputFilepath):
    mapped = {}

    try:
        with open (inputFilepath, mode='r') as file:
            content = csv.reader(file)
            for line in content:
                if (len(line) == 3):
                    mapped[line[0]] = {
                        'item_number': line[1],
                        'uom': line[2]
                    }
    except:
        print('*** Error: Failed to read input file for UOM Master. Please make sure filename is valid. ***')
        return {}
    
    return mapped

def getInventoryMasterData(inputFilepath):
    mapped = {}

    try:
        with open (inputFilepath, mode='r') as file:
            content = csv.reader(file)
            for line in content:
                if (len(line) == 4):
                    mapped[line[1]] = int(line[3]) if line[3].isnumeric() else 0
    except:
        print('*** Error: Failed to read input file for Inventory Master. Please make sure filename is valid. ***')
        return {}

    return mapped

def getOrdersFromInputfile(filepath, uomMaster):
    orders = []
    

    try:
        with open (filepath, mode='r') as file:
            count = 1
            content = csv.reader(file)
            for line in content:
                if count == 1:
                    count += 1
                    continue
        
                if (len(line) == 8):
                    qtyInEach = int(uomMaster[line[0]]['uom']) * int(line[6])
                    order = Order(line[0], '', line[1], line[2], line[3], line[4], line[5], line[6], qtyInEach, line[7])
                    orders.append(order)
                count += 1
    except:
        print('*** Error: Failed to read batch input file. Please make sure filename is valid. ***')
        return [], {}

    return orders

def combineOrders(orders):
    groupedByOrderNumber = {}
    groupedBySKU = {}

    processedOrders = {}
    orderDetails = {
        'totalOrderAmount': 0.0,
        'totalPaidByCustomer': 0.0,
        'totalOrderTax': 0.0,
        'totalShipping': 0.0
    }

    for order in orders:
        # group by Order Number
        if order.orderNumber not in groupedByOrderNumber:
            groupedByOrderNumber[order.orderNumber] = {
                'orderTotal': order.orderTotal,
                'orderPaidByCustomer': order.paidByCustomer,
                'orderTax': order.tax,
                'orderShipping': order.shipping
            }
        # group by SKU
        actualSku = (order.sku).split('-')[0]
        if actualSku in groupedBySKU:
            groupedBySKU[actualSku].append(order)
        else:
            groupedBySKU[actualSku] = [order]

    for sku, orders in groupedBySKU.items():
        totalQty = 0
        totalPrice = 0
        for order in orders:
            totalQty += order.qtyInEach
            totalPrice += order.totalSaleOrder
        processedOrders[sku] = {
            'sku': sku,
            'desc': order.itemDescription,
            'totalQty': int(totalQty),
            'totalPrice': float(totalPrice),
            'pricePerPiece': float(totalPrice) / int(totalQty)
        }

    for orderNumber, order in groupedByOrderNumber.items():
        orderDetails['totalOrderAmount'] += order['orderTotal']
        orderDetails['totalPaidByCustomer'] += order['orderPaidByCustomer']
        orderDetails['totalOrderTax'] += order['orderTax']
        orderDetails['totalShipping'] += order['orderShipping']

    return processedOrders, orderDetails

def getOrdersWithUOMVariants(results, order, caseQty, boxQty):
    caseQty = int(caseQty)
    boxQty = int(boxQty)
    subTotal = 0
    caseNumber = 0
    boxNumber = 0
    eachNumber = 0
    totalQty = order['totalQty']
    itemDesc = order['desc']
    pricePerPiece = order['pricePerPiece']
 
    if caseQty != 0:
        caseNumber = totalQty // caseQty
    if boxQty != 0:
        boxNumber = (totalQty - (caseNumber * caseQty)) // boxQty
    eachNumber = totalQty - (caseNumber * caseQty) - (boxNumber * boxQty)
    
    if caseNumber > 0:
        results.append([
            order['sku'],
            itemDesc,
            'CASE',
            caseNumber,
            round(pricePerPiece, 3)
        ])
        subTotal += (pricePerPiece * caseQty * caseNumber)
    if boxNumber > 0:
        results.append([
            order['sku'],
            itemDesc,
            'BOX',
            boxNumber,
            round(pricePerPiece, 3)
        ])
        subTotal += (pricePerPiece * boxQty * boxNumber)
    if eachNumber > 0:
        results.append([
            order['sku'],
            itemDesc,
            'EA',
            eachNumber,
            round(pricePerPiece, 3)
        ])
        subTotal += (pricePerPiece * eachNumber)
    
    return subTotal

def resultIsValidated(resultDetails, orders, inventoryMaster):
    outOfStockSKUs = []
    isOutOfStock = False

    if round(resultDetails['grandTotal'], 3) != round(resultDetails['totalOrderBeforeDiscount'], 3):
        return False, 'Total Before Discount does not match with Grand Total. Please contact Ecom right away.', []
    
    for sku, orderInfo in orders.items():
        if int(orderInfo['totalQty']) > inventoryMaster[sku]:
            outOfStockSKUs.append(sku)
            isOutOfStock = True
    
    if isOutOfStock:
        return False, 'One or more items are out of stock.', outOfStockSKUs
        
    return True, '', []

def processResult(filepath, uomMaster, inventoryMaster, orders, orderDetails):
    results = []
    grandTotalCrossCheck = 0
    
    for sku, orderInfo in orders.items():
        caseUOM = uomMaster[sku + '-CASE']['uom'] if uomMaster.get(sku + '-CASE') else 0
        boxUOM = uomMaster[sku + '-BOX']['uom'] if uomMaster.get(sku +'-BOX') else 0
        grandTotalCrossCheck += getOrdersWithUOMVariants(results, orders[sku], caseUOM, boxUOM)

    resultDetails = {
        'grandTotal': grandTotalCrossCheck,
        'totalOrderBeforeDiscount': orderDetails['totalOrderAmount'] - orderDetails['totalOrderTax'] - orderDetails['totalShipping'],
        'totalOrderAmount': orderDetails['totalOrderAmount'],
        'totalPaidByCustomer': orderDetails['totalPaidByCustomer'],
        'totalTax': orderDetails['totalOrderTax'],
        'totalShipping': orderDetails['totalShipping']
    }

    dataFrame = pd.DataFrame(results, columns=['SKU', 'Desc', 'UOM', 'QTY', 'PpP'])
    dataFrame.index = dataFrame.index + 1
    # dataFrame.to_excel(filepath, startrow=3, startcol=0) # WORKING

    with pd.ExcelWriter(filepath, engine='xlsxwriter') as writer:
        dataFrame.to_excel(writer, startrow=7, startcol=0)

        worksheet = writer.sheets['Sheet1']
        worksheet.write(0, 0, 'Grand Total: ${:.2f}'.format(resultDetails['grandTotal']))
        worksheet.write(1, 0, 'Order Total Before Discount: ${:.2f}'.format(resultDetails['totalOrderBeforeDiscount']))
        worksheet.write(2, 0, 'Order Total: ${:.2f}'.format(resultDetails['totalOrderAmount']))
        worksheet.write(3, 0, 'Customer Paid: ${:.2f}'.format(resultDetails['totalPaidByCustomer']))
        worksheet.write(4, 0, 'Tax: ${:.2f}'.format(resultDetails['totalTax']))
        worksheet.write(5, 0, 'Shipping: ${:.2f}'.format(resultDetails['totalShipping']))
    
    print('Your batch output file is: ' + filepath)
    
    isValidated, validationMessage, outOfStockSKUs = resultIsValidated(resultDetails, orders, inventoryMaster)
    if not isValidated:
        return False, validationMessage, outOfStockSKUs

    return True, '', []

def validateInputFilename(filename):
    if '.csv' not in filename:
        return filename + '.csv'
    return filename

def getUOMMasterFilepath():
    return os.path.join(ASSETS_BASE_DIR, UOM_MASTER_FILENAME)

def getInventoryMasterFilepath():
    return os.path.join(ASSETS_BASE_DIR, INVENTORY_MASTER_FILENAME)

def batchOrders(inputFilename):
    inputPath = USER_DOWNLOADS + inputFilename
    
    isSuccess = True
    errorMessage = ''
    response = {
        'success': isSuccess,
        'errorMessage': errorMessage,
        'warning': None,
        'warningMessage': None,
        'outOfStockSKUs': [],
        'outputFilename': ''
    }

    batchFilename = validateInputFilename(inputPath)
    uomMasterFilepath = getUOMMasterFilepath()
    inventoryMasterFilepath = getInventoryMasterFilepath()

    uomMaster = getUOMMasterData(uomMasterFilepath)
    inventoryMaster = getInventoryMasterData(inventoryMasterFilepath)

    if not uomMaster or not inventoryMaster:
        errorMessage = "Please check UOM Master: " + uomMasterFilepath
        isSuccess = False
        response["success"] = isSuccess
        response["errorMessage"] = errorMessage
        return response

    if not inventoryMaster:
        errorMessage = "Please check Inventory Master: " + inventoryMasterFilepath
        isSuccess = False
        response["success"] = isSuccess
        response["errorMessage"] = errorMessage
        return response

    orders = getOrdersFromInputfile(batchFilename, uomMaster)

    if not orders:
        errorMessage = "Please check your input batch file: " + inputFilename
        isSuccess = False
        response["success"] = isSuccess
        response["errorMessage"] = errorMessage
        return response

    combinedOrders, orderDetails = combineOrders(orders)

    if not combinedOrders or not orderDetails:
        errorMessage = "Please try again."
        isSuccess = False
        response["success"] = isSuccess
        response["errorMessage"] = errorMessage
        return response

    outputFilename = 'batch_output_{}.xlsx'.format(getTimestamp())

    isWithoutWarning, warningMessage, outOfStockSKUs =  processResult(outputFilename, uomMaster, inventoryMaster, combinedOrders, orderDetails)
    response["warning"] = isWithoutWarning
    response["warningMessage"] = warningMessage
    response["outOfStockSKUs"] = outOfStockSKUs
    response["outputFilename"] = outputFilename
    return response