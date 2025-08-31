import os
import re
import requests
import pandas as pd
from pandas import json_normalize
from dotenv import dotenv_values

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TwitchClipDL:
    def __init__(self, username):
        config = dotenv_values(".env")
        self.client_id = config["CLIENT_ID"]
        self.client_secret = config["CLIENT_SECRET"]
        self.base_url = 'https://api.twitch.tv/helix'

        self.access_token = self._private_get_access_token()
        self.broadcaster_id = self._private_get_user_id(username)

    def _private_get(self, endpoint, params=None):
        url = f'{self.base_url}/{endpoint}'
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Client-Id': self.client_id
        }
        response = requests.get(url, params=params, headers=headers)
        return response
    
    def _private_get_access_token(self):
        url = 'https://id.twitch.tv/oauth2/token'
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials'
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        response = requests.post(url, data=data, headers=headers)
        if response.status_code == 200:
            return response.json()['access_token']

    def _private_get_user_id(self, username):
        params = {
            'login': username
        }
        response = self._private_get(endpoint='users', params=params)
        if response.status_code == 200:
            data = response.json()
            if data['data']:    
                return data['data'][0]['id']
            else:
                return None
        else:
            return None
        
    def get_data_from_twitch(self, pandas_df=False):
        data_list = []
        cursor = None

        while True:
            params = {
                "broadcaster_id": self.broadcaster_id,
                "first": 100,
            }
            if cursor:
                params["after"] = cursor

            response = self._private_get(endpoint="clips", params=params)
            response.raise_for_status()
            data = response.json()

            data_list.extend(data["data"])

            cursor = data.get("pagination", {}).get("cursor")
            if not cursor:
                break

        if pandas_df:
            return json_normalize(data_list).sort_values(by="created_at", ascending=True)
        else:
            return data_list


    def _private_sanitize_filename(self, name: str) -> str:
        return re.sub(r'[\\/*?:"<>|]', "_", name.strip()).lower()

    def _private_get_clips(self, row):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')

        self.driver = webdriver.Chrome(options=options)
        self.driver.get(row.url)

        wait = WebDriverWait(self.driver, 10)  

        video_element = wait.until(
            EC.presence_of_element_located((By.TAG_NAME, 'video'))
        )

        wait.until(lambda d: video_element.get_attribute('src') is not None)

        clip_url = video_element.get_attribute('src')

        self.driver.quit()

        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(clip_url, headers=headers, stream=True)
        filename = f"clips/{self._private_sanitize_filename(row.title)}-{row.id}.mp4"

        try:
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            print(f"Clip salvo em {filename}")
        except Exception as e:
            print(f"Falha ao baixar o clip: {e}")

    def get_clips(self, clips_df=None):
        if clips_df is None:
            clips_df = self.get_data_from_twitch(pandas_df=True)
        clips_df.apply(self._private_get_clips, axis=1)
        
        
        