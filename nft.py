from opensea import Assets
from opensea import Collections
import threading
import os
import json
import requests
import concurrent.futures

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

owner_address = os.getenv('address')
api_key = os.getenv('opensea_api_key')

base_assets_url = 'https://api.opensea.io/api/v1/assets?' if os.getenv('env') == 'prod' else 'https://testnets-api.opensea.io/assets?'
base_collection_url = 'https://api.opensea.io/collection/' if os.getenv('env') == 'prod' else 'https://testnets-api.opensea.io/collection/'
headers = {'X-API-KEY': api_key}


def get_collection(collection_name):

    asset_contract_url = base_collection_url+collection_name
    print(asset_contract_url)
    response = requests.request("GET", asset_contract_url, headers=headers)
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
        # To ensure clearly listed asset is not of auction type but rather clear set price
        if asset['sell_orders'][0]['payment_token_contract']['id'] == 1:
            return float(asset["sell_orders"][0]['current_price'])/1000000000000000000
        else:
            token_id = asset['token_id']
            print(f'{token_id} has token contract 2')
            return None
    else:
        return None

def fire_url(url):
    print(f'Firing url {url}')
    s = requests.Session()
    try:
        retries = Retry(total=2, backoff_factor=1, status_forcelist=[ 404, 429, 503, 504 ])
        s.mount('https://', HTTPAdapter(max_retries=retries))
        response = s.get(url, headers=headers)
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


    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_url = {executor.submit(fire_url, url): url for url in urls}
        future = executor.submit(fire_url, url)
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            result = future.result()
            if result:
                assets = assets + future.result()
            else:
                print(result)


    print('Checking for assets')
    if len(assets) == 0:
        return 'No assets in this collection'


    min_list_price = 10000000000000.0
    found_floor = False
    floor_token_id = ''
    debug_json = {}
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
                                floor_token_id = token_id
                                found_floor = True
                                min_list_price = price
                                debug_json = asset
                                print(f'New floor price is {min_list_price}')
        except:
            continue

    if found_floor:
        # print(debug_json)
        link = f'https://opensea.io/assets/{address}/{floor_token_id}'
        return f'Floor price for {trait_value} is {min_list_price}. {link}'
    else:
        return f'Could not find floor in scanned items'



async def get_floor_price(collection_name, prop, prop_val):
    try:
        address, floor_price, supply = get_collection_stats(collection_name) #'crypto-dino-v3'
        if not prop:
            return f'Floor price of {collection_name} is {floor_price}'
        print(f'Supply is {supply}')

        try:
            f = open(f'collections/{collection_name}.json')
        except:
            return 'Your collection is not supported yet.'

        coll_json = json.load(f)
        props  = coll_json['collection']['traits'].keys()

        props = [p.lower() for p in props]
        if prop not in props:
            return f'Invalid property name. Here is a list {list(props)}'

        prop_vals = coll_json['collection']['traits'][prop].keys()
        prop_vals = [v.lower() for v in prop_vals]
        if prop_val not in prop_vals:
            return f'Invalid property value. Here is a list {list(prop_vals)}'

        return get_floor_price_by_property(address, prop, prop_val, supply)
    except Exception as e:
        print(str(e))
        return 'Error! Make sure collection name is correct and property name and val exist.'
