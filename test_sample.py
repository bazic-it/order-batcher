# Created: 9/17/2024
# Last updated: 9/20/2024

import os
import pytest
from script import *

TEST_ASSETS_BASE_DIR = './assets/test/'
TEST_UOM_MASTER_FILENAME = 'test_uom_input_compact.csv'
TEST_INVENTORY_MASTER_FILENAME = 'test_inventory_master_compact.xlsx'
TEST_BATCH_INPUT_FILENAME = 'shipstation_input.csv'

def test_validateInputFilename():
    testFilename1 = "test.csv"
    testFilename2 = "test"

    res1 = validateInputFilename(testFilename1)
    res2 = validateInputFilename(testFilename2)

    assert res1 == USER_DOWNLOADS + "test.csv"
    assert res2 == USER_DOWNLOADS + "test.csv"

def test_getUOMMasterData():
    expected = {
            'SKU': {
                'item_number': 'Item',
                'uom': 'Uom',
            },
            '00402-EACH': {
                'item_number': '402',
                'uom': '1',
            },
            '01707-CASE': {
                'item_number': '1707',
                'uom': '48',
            },
            '01707-SET2': {
                'item_number': '1707',
                'uom': '2',
            },
            '1220-PACK2': {
                'item_number': '1220',
                'uom': '2',
            },
            '1228-BOX': {
                'item_number': '1228',
                'uom': '24',
            },
            '1245-CASE': {
                'item_number': '1245',
                'uom': '144',
            },
            'S-2-BOX': {
                'item_number': 'S-2',
                'uom': '24',
            },
            'S-2-CASE': {
                'item_number': 'S-2',
                'uom': '480',
            },
            'S-2-EACH': {
                'item_number': 'S-2',
                'uom': '1',
            },
            'S-2-PACK4': {
                'item_number': 'S-2',
                'uom': '4',
            }
        }

    path = os.path.join(TEST_ASSETS_BASE_DIR, TEST_UOM_MASTER_FILENAME)
    res = getUOMMasterData(path)

    assert res == expected

def test_getInventoryMasterData():
    expected = {
        '1707': 162,
        '1011': 10408,
        '1019': 7469,
        '102269': 305,
        'S-2': 22717
    }

    path = os.path.join(TEST_ASSETS_BASE_DIR, TEST_INVENTORY_MASTER_FILENAME)
    res = getInventoryMasterData(path)
    
    assert res == expected

def test_getOrdersFromInputfile():
    uomPath = os.path.join(TEST_ASSETS_BASE_DIR, TEST_UOM_MASTER_FILENAME)
    inputPath = os.path.join(TEST_ASSETS_BASE_DIR + TEST_BATCH_INPUT_FILENAME)

    uomMaster = getUOMMasterData(uomPath)
    orders, message = getOrdersFromInputfile(inputPath, uomMaster)

    order = orders[0]
    assert message == ''
    assert order.sku == 'S-2-PACK4'
    assert order.itemDescription == ''
    assert order.itemPrice == 7.09
    assert order.orderNumber == '113-7604483-9257052'
    assert order.totalSaleOrder == (7.09*2)
    assert order.orderTotal == 7.59
    assert order.paidByCustomer == 7.59
    assert order.tax == 0.5
    assert order.itemQty == 2
    assert order.qtyInEach == (4*2)
    assert order.shipping == 0