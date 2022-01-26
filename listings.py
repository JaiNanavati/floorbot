import requests
import os

base_assets_url = 'https://api.opensea.io/api/v1/assets?' if os.getenv('env') == 'prod' else 'https://testnets-api.opensea.io/assets?'
base_collection_url = 'https://api.opensea.io/collection/' if os.getenv('env') == 'prod' else 'https://testnets-api.opensea.io/collection/'
base_orders_url = 'https://api.opensea.io/wyvern/v1/orders?' if os.getenv('env') == 'prod' else 'https://testnets-api.opensea.io/wyvern/v1/orders'
api_key =  os.getenv('API_KEY')
headers = {'X-API-KEY': api_key}



def get_listings(slug):
    print(api_key)
    bundled = 'false'
    is_english = 'false'
    include_bundled='false'
    limit=50
    asset_contract_address='0xfe8c6d19365453d26af321d0e8c910428c23873f'
    order_url = f'{base_orders_url}bundled={bundled}&is_english={is_english}&limit={limit}&asset_contract_address={asset_contract_address}'
    response = requests.request("GET", order_url, headers=headers)
    print(response.status_code)
    print(response.json())


get_listings('slug')
