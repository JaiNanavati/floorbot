from opensea import Assets
from opensea import Collections
import threading
import os
import json
import requests
import concurrent.futures

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry




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
        print('Successfully collected data')
        return response.json()
    else:
        print(f'Collection call failed with status code {response.status_code}')
        return None


def get_collection_stats(collection_name):
    print(f'Grabbing stats for {collection_name}')
    collection = get_collection(collection_name)
    if collection:
        contract_address = collection['collection']['primary_asset_contracts'][0]['address']
        print(f'Contract Address is: {contract_address}')

        floor_price = collection['collection']['stats']['floor_price']
        print(f'Floor price is: {floor_price}')

        supply = collection['collection']['stats']['total_supply']
        print(f'Total supply is: {supply}')

        return contract_address, floor_price, supply
    else:
        raise Exception()
        print('No collection by that name')

def grab_price(asset):
    if asset['sell_orders'] != None:
        return float(asset["sell_orders"][0]['current_price'])/1000000000000000000
    else:
        return None

def fire_url(url):
    print(f'Firing url {url}')
    s = requests.Session()
    try:
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[ 429, 503, 504 ])
        s.mount('https://', HTTPAdapter(max_retries=retries))
        response = s.get(url)
        if response.status_code == 200:
            return response.json()['assets']
        else:
            print(f'Failed to retrieve assets {response.status_code}')
            raise Exception()
    except:
        return None


def get_floor_price_by_property(address, trait_type, trait_value, collection_count):
    print(f'Trait type {trait_type}, Trait value {trait_value}')
    assets = []
    futures = []
    urls = []
    limit = 50
    offset = 0
    while offset <= collection_count:
        url = base_assets_url + f'asset_contract_address={address}&offset={offset}&limit={limit}&order_direction=asc'
        urls.append(url)
        offset = offset+limit+1


    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(fire_url, url): url for url in urls}
        future = executor.submit(fire_url, url)
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            result = future.result()
            if result:
                assets = assets + future.result()


    print('Checking for assets')
    if len(assets) == 0:
        return 'No assets in this collection'


    min_list_price = 10000000000000.0
    for asset in assets:
        try:
            price = grab_price(asset)
            if price != None:
                token_id = asset['token_id']
                traits = asset['traits']
                for trait in traits:
                    if trait['trait_type'].lower() == trait_type.lower():
                        if trait['value'].lower() == trait_value.lower():
                            if min_list_price > price:
                                 min_list_price = price
                                 print(f'New floor price is {min_list_price}')
        except:
            continue

    print(f'Floor price for {trait_value} is {min_list_price}')
    return min_list_price


def get_floor_price(collection_name, prop, prop_val):
    try:
        address, floor_price, supply = get_collection_stats(collection_name) #'crypto-dino-v3'
        if not prop:
            return f'Floor price of {collection_name} is {floor_price}'
        return get_floor_price_by_property(address, prop, prop_val, supply)
    except:
        return 'Error! Make sure collection name is correct and property name and val exist.'
    # get_floor_price_by_property(address, 'Fin', 'fin_yellow', 1390)


# fin Fin Yellow
# get_asset_by_token_id('0xcc14dd8e6673fee203366115d3f9240b079a4930','916')
