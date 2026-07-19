import inquirer
import logging
from argparse import ArgumentParser
from requests import Session
from os import listdir, path
from .get_bearer_token import get_bearer_token

logger = logging.getLogger(__name__)

BASE_URL = 'https://api.listonic.com'
IMAGE_EXTENSION = '.png'

def main() -> bool:
    logging.basicConfig(level=logging.INFO)

    parser = ArgumentParser()
    parser.add_argument('--image-path', default='.')
    image_path: str = parser.parse_args().image_path

    access_token = get_bearer_token(BASE_URL)

    session = Session()
    session.headers.update({'Authorization': f'Bearer {access_token}'})

    # get lists from listonic
    resp_lists = session.get(f'{BASE_URL}/api/lists')
    if resp_lists.status_code == 401: exit('Bearer token expired!')
    lists = resp_lists.json()
    ordered_lists: list[dict[str, str]] = [
        {'name': list['Name'], 'url': list['Url']}
        for list in sorted(lists, key=lambda l: l['SortOrder'], reverse=True)
    ]

    # promt lists
    answer: dict[str, str] | None = inquirer.prompt([
        inquirer.List(
            name='list',
            message='Select a list to use',
            choices=[f'{index+1}. {list['name']}'
                    for index, list in enumerate(ordered_lists)]
        ),
        inquirer.Text(
            name='default-description',
            message='Products default description (optional)'
        )
    ])
    if not answer: return False

    answer_index = int(answer['list'].split('.')[0])-1
    selected_list = ordered_lists[answer_index]

    default_description = answer['default-description']

    # get images, by default from the current folder
    images = [i for i in listdir(image_path) if i.endswith(IMAGE_EXTENSION)]

    # add items and images to listonic
    for image in images:
        base_name = image[:-len(IMAGE_EXTENSION)]
        item = list(map(str.strip, base_name.split('#', maxsplit=1)))
        name, description = ([item[0], default_description]
                             if len(item) < 2 else [item[0], item[1]])

        item_json = { 'name': name, 'description': description }
        resp_item = session.post(f'{BASE_URL}{selected_list['url']}/items',
                                json=item_json)
        if resp_item.status_code != 201:
            logger.error(f'Error while creating item: {name}')
            continue
        item_url = resp_item.json()['Url']

        file = open(path.join(image_path, image), 'rb')
        resp_image = session.post(f'{BASE_URL}{item_url}/images', data=file)
        file.close()
        if resp_image.status_code != 200:
            logger.error(f'Error while uploading image: {image}')
            continue
        print(f'Uploaded {image} image')

    print('Upload completed!')
    return True
