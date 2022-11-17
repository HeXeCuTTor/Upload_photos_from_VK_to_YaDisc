import requests
from pprint import pprint
import json
import time
from tqdm import tqdm
from config import token, access_token

class VK:
    def __init__(self, access_token, user_id, version='5.131'):
       self.token = access_token
       self.id = user_id
       self.version = version
       self.params = {'access_token': self.token, 'v': self.version}

    def users_photo(self):
       url = 'https://api.vk.com/method/photos.get'
       params = {'owner_id': self.id, 'album_id': 'profile', 'photo_sizes': 0, 'extended': 1, 'rev': 1}
       response = requests.get(url, params={**self.params, **params})
       return response.json()

class YaUploader:
    def __init__(self, token: str):
        self.token = token

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': f'OAuth {self.token}'
        }

    def create_folder(self, file_path):
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources/"
        headers = self.get_headers()
        params = {'path': file_path}
        responce = requests.put(upload_url, headers = headers, params = params)
        return responce
        
    def upload(self, file_path, filename):
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        headers = self.get_headers()
        params = {'path': file_path, 'url': filename}
        source = requests.post(upload_url, headers = headers, params = params)
        source_getted = source.json()
        return source_getted


s = 1
while s == 1:
    start = input("Добавить новые фото? (Да/Нет) ").lower()
    if start == 'да':
        user_id = input("Введите id пользователя VK: ")
        folder = input("Введите название папки Яндекс Диск, в которую требуется сохранить фотографии: ")
        uploader = YaUploader(token)
        uploader.create_folder(folder) 
        vk = VK(access_token, user_id)
        photos_data = vk.users_photo()
        photos_json = []
        photo_data = {}
        for items in photos_data.values():
            for keys,values in items.items():
                if keys == 'items':
                    for list in values:
                        for key, value in list.items():
                            if key == 'likes':
                                likes = value.get('count')
                            if key == 'date':
                                date = value
                            if key == 'sizes':
                                photo_data['sizes'] = value[-1].get('type')
                                photo_data['url'] = value[-1].get('url')      
                        photo_data['file_name'] = f'{likes}_{date}'
                        photos_json.append(photo_data)
                        photo_data = {}
        sorted_photos_json = (sorted(photos_json, key=lambda d: d['sizes']))[-5:]
        for link in sorted_photos_json:
            photo_link = link.get('url')
            name = link.get('file_name')
            uploader.upload(f'{folder}/{name}',photo_link)
            link.pop('url')
        for i in tqdm(sorted_photos_json,desc = "Загрузка фото "):
            time.sleep(.5)
        with open ('list_photos.json', 'w') as f:
            json.dump(sorted_photos_json, f, sort_keys=True, ensure_ascii = False, indent = 2)
    elif start == 'нет':
        s = 0
    else:
        print("Неверный формат данных")