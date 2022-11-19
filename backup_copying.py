import requests
import json
from tokens import Token_vk
from pprint import pprint
from tqdm import tqdm

user_id = input('Введите id пользователя VK: ')
Token_ya = input('Введите токен с Я.Полигона: ')

URL_id_photo = 'https://api.vk.com/method/photos.get'
params_id_photo = {
    'owner_id': user_id,
    'album_id': 'profile',
    'access_token': Token_vk,
    'v': '5.131',
    'extended': '1',
    'count': '5',
}
response_id_photo = requests.get(URL_id_photo, params=params_id_photo)
data_id_photo = response_id_photo.json()

URL_id_info = 'https://api.vk.com/method/users.get'
params_id_info = {
    'user_ids': user_id,
    'access_token': Token_vk,
    'v': '5.131'
}
response_id_info = requests.get(URL_id_info, params=params_id_info)
data_id_info = response_id_info.json()

for items in data_id_info['response']:
    name = items['first_name'] + '_' + items['last_name']
name_of_directory = f'/{name}'

all_files = []

for photos in tqdm(data_id_photo['response']['items'], desc='Loading to file json'):
    file_information = {}
    file_information['file_name'] = str(photos['likes']['count']) + '.jpg'
    file_information['type'] = photos['sizes'][-1]['type']
    file_information['link'] = photos['sizes'][-1]['url']
    all_files.append(file_information)

info_file = open('files.json', 'wt', encoding='UTF-8')
json.dump(all_files, info_file, ensure_ascii=False, indent=1)
info_file.close()


class YaUpLoader:
    base_host = 'https://cloud-api.yandex.net/'

    def __init__(self, token):
        self.token = token

    def get_headers(self):
        return {
            "Content-Type": 'application/json',
            'Authorization': f'OAuth {self.token}'
        }

    def get_upload_link(self, path):
        uri = 'v1/disk/resources/upload'
        request_url = self.base_host + uri
        params = {'path': path}
        response = requests.get(request_url, headers=self.get_headers(), params=params)
        print(response.json())
        return response.json()['href']

    def create_directory(self, yandex_path):
        uri = 'v1/disk/resources'
        requests_url = self.base_host + uri
        params = {'path': yandex_path}
        requests.put(requests_url, headers=self.get_headers(), params=params)

    def upload_from_url(self, url, yandex_path):
        uri = 'v1/disk/resources/upload'
        requests_url = self.base_host + uri
        params = {'url': url, 'path': yandex_path}
        requests.post(requests_url, params=params, headers=self.get_headers())


if __name__ == '__main__':
    ya = YaUpLoader(Token_ya)
    ya.create_directory(name_of_directory)

    for photos in tqdm(all_files, desc='Loading to Я.Диск'):
        name = photos['file_name']
        photo_url = photos['link']
        ya.upload_from_url(photo_url, f'{name_of_directory}/{name}')

file_json = open('files.json', encoding='UTF-8')
pprint(json.load(file_json))
file_json.close()