from opensea import Assets
from opensea import Collections
import os
import json
import requests
from concurrent.futures import ThreadPoolExecutor as PoolExecutor




contract_address='0xcc14dd8e6673fee203366115d3f9240b079a4930'
ludo_labs = 'ludo-labs'
owner_address = os.getenv('address')
base_url = 'https://rinkeby-api.opensea.io/api/v1/'
coll_ep = "https://api.opensea.io/collection/"
assets_ep = "https://api.opensea.io/api/v1/assets"
base_assets_url = 'https://testnets-api.opensea.io/assets?'
base_collection_url = 'https://testnets-api.opensea.io/collection/'


api = Assets()

collections = Collections()


def get_assets_by_owner(owner_address):
    assets_response = api.fetch(owner=owner_address)
    assets = assets_response['assets']

    for asset in assets:
        if ludo_labs in asset['collection']['slug']:
            for trait in asset['traits']:
                type = trait['trait_type']
                value = trait['value']
                print(f'Type {type} value {value}')
                print('\n')

def get_asset_price_by_token_id(asset_contract_address, token_id):

    url = f'https://testnets-api.opensea.io/asset/{asset_contract_address}/{token_id}/'
    response = requests.request("GET", url)

    if response.status_code == 200:
        try:
            list_price = float(response.json()["orders"][0]['current_price'])/1000000000000000000
            return list_price
        except:
            return None


def get_collection(collection_name):

    asset_contract_url = base_collection_url+collection_name
    response = requests.request("GET", asset_contract_url)
    if response.status_code == 200:
        return response.json()
    else:
        return None


def get_collection_stats(collection_name):
    collection = get_collection(collection_name)
    if collection:
        contract_address = collection['collection']['primary_asset_contracts'][0]['address']
        floor_price = collection['collection']['stats']['floor_price']
        print(f'Contract Address is: {contract_address}')
        print(f'Floor price is: {floor_price}')
        return contract_address
    else:
        print('No collection by that name')

def grab_price(asset):
    if asset['sell_orders'] != None:
        return float(asset["sell_orders"][0]['current_price'])/1000000000000000000
    else:
        return None

def fire_url(url):
    response = requests.request("GET", url)
    if response.status_code == 200:
        return response.json()
    else:
        return None


def get_floor_price_by_property(address, trait_type, trait_value, collection_count):
    assets = []
    limit = 50
    offset = 0
    while offset <= collection_count:
        url = base_assets_url + f'asset_contract_address={address}&offset={offset}&limit={limit}&order_direction=asc'
        response = requests.request("GET", url)
        if response.status_code == 200:
            assets = assets + response.json()['assets']
        else:
            break
        offset = offset+limit+1

    if len(assets) == 0:
        return 'No assets in this collection'


    min_list_price = 10000000000000.0
    for asset in assets:
        print(asset['token_id'])
        try:
            price = grab_price(asset)
            if price != None:
                token_id = asset['token_id']
                traits = asset['traits']
                for trait in traits:
                    if trait['trait_type'] == trait_type:
                        if trait['value'] == trait_value:
                            if min_list_price > price:
                                 min_list_price = price
                                 print(f'New floor price is {min_list_price}')
        except:
            continue

    print(f'Floor price for {trait_value} is {min_list_price}')
    return min_list_price


def get_floor_price(collection_name):
    address = get_collection_stats(collection_name) #'crypto-dino-v3'
    return get_floor_price_by_property(address, 'Fin', 'fin_yellow', 1390)


# fin Fin Yellow
# get_asset_by_token_id('0xcc14dd8e6673fee203366115d3f9240b079a4930','916')
