import inquirer
import logging
import requests
from argparse import ArgumentParser
from os import getenv, listdir, path

logger = logging.getLogger(__name__)

BASE_URL = 'https://api.listonic.com'
IMAGE_EXTENSION = '.png'

def main() -> bool:
    logging.basicConfig(level=logging.INFO)

    parser = ArgumentParser()
    parser.add_argument('--image-path', default='.')
    args = parser.parse_args()

    BEARER_TOKEN = getenv('BEARER_TOKEN')
    if not BEARER_TOKEN:
        logger.critical('Missing environment variable')
        return False

    session = requests.Session()
    session.headers.update({'Authorization': f'Bearer {BEARER_TOKEN}'})

    # get lists from listonic
    resp_lists = session.get(f'{BASE_URL}/api/lists')
    if resp_lists.status_code == 401: exit('Bearer token expired!')
    lists = resp_lists.json()
    ordered_lists = [
        {'name': list['Name'], 'url': list['Url']}
        for list in sorted(lists, key=lambda l: l['SortOrder'], reverse=True)
    ]

    # promt lists
    answer = inquirer.prompt([inquirer.List(
        name='list',
        message='Select a list to use',
        choices=[f'{index+1}. {list['name']}'
                 for index, list in enumerate(ordered_lists)]
    )])
    if not answer: return False

    answer_index = int(answer['list'].split('.')[0])-1
    selected_list = ordered_lists[answer_index]

    # get images, by default from the current folder
    images = [i for i in listdir(args.image_path)
              if i.endswith(IMAGE_EXTENSION)]

    # add items and images to listonic
    for image in images:
        item_name = image[:-len(IMAGE_EXTENSION)]
        resp_item = session.post(f'{BASE_URL}{selected_list['url']}/items',
                                json={'name': item_name})
        if resp_item.status_code != 201:
            logger.error(f'Error while creating item: {item_name}')
            continue
        item_url = resp_item.json()['Url']

        file = open(path.join(args.image_path, image), 'rb')
        resp_image = session.post(f'{BASE_URL}{item_url}/images', data=file)
        file.close()
        if resp_image.status_code != 200:
            logger.error(f'Error while uploading image: {image}')
            continue
        print(f'Uploaded {image} image')

    print('Upload completed!')
    return True
