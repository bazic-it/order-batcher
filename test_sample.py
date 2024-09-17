# Created: 9/17/2024
# Last updated: 9/17/2024

import os
import pytest
from script import *

TEST_ASSETS_BASE_DIR = './assets'
TEST_UOM_MASTER_FILENAME = 'uom_input.csv'
TEST_INVENTORY_MASTER_FILENAME = 'inventory_input.xlsx'

def test_validateInputFilename():
    testFilename1 = "test.csv"
    testFilename2 = "test"

    res1 = validateInputFilename(testFilename1)
    res2 = validateInputFilename(testFilename2)

    assert res1 == "test.csv"
    assert res2 == "test.csv"

def test_getUOMMasterData():
    expected = {
            'SKU': {
                'item_number': 'Item',
                'uom': 'Uom',
            },
            '5076-BOX': {
                'item_number': '5076',
                'uom': '24',
            },
            '5076-CASE': {
                'item_number': '5076',
                'uom': '72',
            },
            '5076-EACH': {
                'item_number': '5076',
                'uom': '1',
            }
        }

    path = os.path.join(TEST_ASSETS_BASE_DIR, TEST_UOM_MASTER_FILENAME)
    res = getUOMMasterData(path)

    assert res == expected

def test_getInventoryMasterData():
    expected = {
        '5076': 11826,
        '5077-A': 8099,
        'S-2': 22913
    }

    path = os.path.join(TEST_ASSETS_BASE_DIR, TEST_INVENTORY_MASTER_FILENAME)
    res = getInventoryMasterData(path)
    
    assert res == expected

def test_getOrdersFromInputfile():
    # getOrdersFromInputfile()
    pass