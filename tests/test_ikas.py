from operator import le
from ikas import Ikas
from dotenv import load_dotenv
import os
import pytest
import random
import datetime
now = datetime.datetime.now()
name_prefix = f'{now.hour}{now.minute}{now.second}'

if os.getenv('_PYTEST_RAISE', "0") != "0":

    @pytest.hookimpl(tryfirst=True)
    def pytest_exception_interact(call):
        raise call.excinfo.value

    @pytest.hookimpl(tryfirst=True)
    def pytest_internalerror(excinfo):
        raise excinfo.value


def test_ikas_auth():
    """Testing if client is able to get access token"""
    ikas_client = Ikas(os.getenv('SHOP_NAME'), os.getenv('CLIENT_ID'), os.getenv('CLIENT_SECRET'))
    assert type(ikas_client.access_token) == str
    client = ikas_client

def test_ikas_list_sales_channels():
    """Testing if client is able to get sales channels"""
    ikas_client = Ikas(os.getenv('SHOP_NAME'), os.getenv('CLIENT_ID'), os.getenv('CLIENT_SECRET'))
    sales_channels = ikas_client.list_sales_channels()
    assert type(sales_channels) == dict
    assert len(sales_channels['data']['listSalesChannel']) > 0
    assert type(sales_channels['data']['listSalesChannel'][0]['id']) == str 
    return sales_channels

def test_ikas_list_stock_locations():
    """Testing if client is able to get stock loactions"""
    ikas_client = Ikas(os.getenv('SHOP_NAME'), os.getenv('CLIENT_ID'), os.getenv('CLIENT_SECRET'))
    stock_locations = ikas_client.list_stock_locations()
    assert type(stock_locations) == dict
    assert len(stock_locations['data']['listStockLocation']) > 0
    assert type(stock_locations['data']['listStockLocation'][0]['id']) == str 
    return stock_locations
    
def test_ikas_save_product():
    """Testing if client is able to create a product"""
    ikas_client = Ikas(os.getenv('SHOP_NAME'), os.getenv('CLIENT_ID'), os.getenv('CLIENT_SECRET'))
    product = ikas_client.save_product({
        'name': 'API TESTING',
        'type': 'PHYSICAL',
        'variants': [{
            'prices': [{
                'sellPrice': 99.9
            }]
        }]
    })
    
    assert type(product) == dict
    assert type(product['data']['saveProduct']['id']) == str

    
def test_ikas_save_variant_type(client=None):
    if client is None:
        ikas_client = Ikas(os.getenv('SHOP_NAME'), os.getenv('CLIENT_ID'), os.getenv('CLIENT_SECRET'))
    else:
        ikas_client = client
        
    variant_type = ikas_client.save_variant_type({
        'name': f'Renk {name_prefix}',
        'selectionType': 'CHOICE',
        'values': [
            {'name': f'Renk {random.randint(0, 100)}'},
            {'name': f'Renk {random.randint(0, 100)}'},
            {'name': f'Renk {random.randint(0, 100)}'},
            {'name': f'Renk {random.randint(0, 100)}'},
            {'name': f'Renk {random.randint(0, 100)}'},
        ]
    })
    assert type(variant_type) == dict
    assert type(variant_type['data']['saveVariantType']['id']) == str
    assert len(variant_type['data']['saveVariantType']['values']) == 5
    return variant_type['data']['saveVariantType']

def test_ikas_create_product_with_multiple_variants():
    """Testing if client is able to create variant types"""  
    ikas_client = Ikas(os.getenv('SHOP_NAME'), os.getenv('CLIENT_ID'), os.getenv('CLIENT_SECRET'))
    variant_type = test_ikas_save_variant_type(ikas_client)
    
    """Testing if client is able to create products with multiple variants"""
    variants = []
    for i in range(0,5):
        variants.append({
            'sku': ''.join(random.choice('0123456789ABCDEF') for i in range(8)),
            'isActive': True,
            'sellIfOutOfStock': False,
            'variantValueIds': [{
                'variantTypeId': variant_type['id'],
                'variantValueId': variant_type['values'][i]['id']
            }],
            'prices': [{
                'sellPrice': 99.9
            }]
        })
    sales_channels = test_ikas_list_sales_channels()
    product = ikas_client.save_product({
        'name': f'API TESTING {name_prefix}',
        'type': 'PHYSICAL',
        'groupVariantsByVariantTypeId': variant_type['id'],
        'salesChannelIds': sales_channels['data']['listSalesChannel'][0]['id'],
        'productVariantTypes': [{
            'order': 0,
            'variantTypeId': variant_type['id'],
            'variantValueIds': [ sub['id'] for sub in variant_type['values']]
            }],
        
        'variants': variants
    })
    
    assert type(product) == dict
    assert type(product['data']['saveProduct']['id']) == str
    assert len(product['data']['saveProduct']['variants']) == 5
    assert type(product['data']['saveProduct']['variants'][0]['id']) == str
    assert type(product['data']['saveProduct']['variants'][0]['sku']) == str
    
    
    for variant in product['data']['saveProduct']['variants']:
        image_res = ikas_client.upload_image(variant['id'], 'https://picsum.photos/500/500')
        
    check_product = ikas_client.list_products({
        'id': {
            'eq': product['data']['saveProduct']['id']
        }
    })
    
    assert check_product['data']['listProduct']['count'] == 1
    assert len(check_product['data']['listProduct']['data'][0]['variants'][0]['images']) == 1
    
    # ADD STOCKS
    list_stock = test_ikas_list_stock_locations()['data']['listStockLocation'][0]
    
    stocks = []
    for variant in product['data']['saveProduct']['variants']:
        stocks.append({
            'productId': product['data']['saveProduct']['id'],
            'variantId': variant['id'],
            'stockCount': random.randint(0,10),
            'stockLocationId': list_stock['id']
        })
    ikas_client.save_product_locations(stocks)
    
    check_product = ikas_client.list_products({
        'id': {
            'eq': product['data']['saveProduct']['id']
        }
    })
    
    assert len(check_product['data']['listProduct']['data'][0]['variants'][0]['stocks']) == 1
    
    