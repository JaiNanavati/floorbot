import requests
import os
import uuid

from nft import get_collection
from PIL import Image
import shutil


base_assets_url = 'https://api.opensea.io/api/v1/assets?' if os.getenv('env') == 'prod' else 'https://testnets-api.opensea.io/assets?'
api_key =  os.getenv('API_KEY')
headers = {'X-API-KEY': api_key}



def get_image_urls(assets):
    images = []
    for asset in assets:
        images.append(asset['image_url'])
    return images


def create_gif(images):
    opened_images = []
    for image in images:
        filename = 'downloads/'+str(uuid.uuid1())+'.png'
        print(image)
        response = requests.get(image)
        file = open(filename, "wb")
        file.write(response.content)
        file.close()

        opened_image = Image.open(filename)
        opened_images.append(opened_image)

    gif_name = f'gifs/{str(uuid.uuid1())}.gif'
    opened_images[0].save(gif_name,save_all=True,append_images=opened_images[1:], optimize=False, duration=500, loop=0)
    return gif_name


def get_images(owner_address, slug=None):
    if slug:
        collection = get_collection(slug)
        if not collection:
            return 'No collection by that slug'

        contract_address = collection['collection']['primary_asset_contracts'][0]['address']
        asset_contract_url = f'{base_assets_url}asset_contract_address={contract_address}&owner={owner_address}'
    else:
        asset_contract_url = f'{base_assets_url}owner={owner_address}'

    assets_response = requests.request("GET", asset_contract_url, headers=headers)
    if assets_response.status_code == 200:
        images = get_image_urls(assets_response.json()['assets'])
        if len(images) != 0:
            return create_gif(images)
        else:
            return 'No nfts of this type'
    else:
        return 'Trouble returning assets. Check address provided'




# get_images('ludo-labs-genesis-collection', '0x0cd645ddaaa85e079251a3694713beebc595cf00')
