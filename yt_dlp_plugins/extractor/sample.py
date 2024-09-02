# coding: utf-8
from __future__ import unicode_literals

import string
import random
import time
import json
import cloudscraper
from bs4 import BeautifulSoup

# Import InfoExtractor and utilities from yt_dlp
from yt_dlp.extractor.common import InfoExtractor
from yt_dlp.utils import js_to_json, urljoin


class DoodStreamIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?dood\.(?:to|watch)/[ed]/(?P<id>[a-z0-9]+)'
    _TESTS = [{
        'url': 'http://dood.to/e/5s1wmbdacezb',
        'md5': '4568b83b31e13242b3f1ff96c55f0595',
        'info_dict': {
            'id': '5s1wmbdacezb',
            'ext': 'mp4',
            'title': 'Kat Wonders - Monthly May 2020',
            'description': 'Kat Wonders - Monthly May 2020 | DoodStream.com',
            'thumbnail': 'https://img.doodcdn.com/snaps/flyus84qgl2fsk4g.jpg',
        }
    }, {
        'url': 'http://dood.watch/d/5s1wmbdacezb',
        'md5': '4568b83b31e13242b3f1ff96c55f0595',
        'info_dict': {
            'id': '5s1wmbdacezb',
            'ext': 'mp4',
            'title': 'Kat Wonders - Monthly May 2020',
            'description': 'Kat Wonders - Monthly May 2020 | DoodStream.com',
            'thumbnail': 'https://img.doodcdn.com/snaps/flyus84qgl2fsk4g.jpg',
        }
    }, {
        'url': 'https://dood.to/d/jzrxn12t2s7n',
        'md5': '3207e199426eca7c2aa23c2872e6728a',
        'info_dict': {
            'id': 'jzrxn12t2s7n',
            'ext': 'mp4',
            'title': 'Stacy Cruz Cute ALLWAYSWELL',
            'description': 'Stacy Cruz Cute ALLWAYSWELL | DoodStream.com',
            'thumbnail': 'https://img.doodcdn.com/snaps/8edqd5nppkac3x8u.jpg',
        }
    }]

    def __init__(self):
        self.scraper = self.create_random_scraper()

    # Function to load user agents from browsers.json
    def load_user_agents(self):
        with open('/content/cloudscraper/cloudscraper/user_agent/browsers.json', 'r') as file:
            data = json.load(file)
            return data['user_agents']['desktop']['windows']['chrome']

    # Function to create a scraper with a random user agent
    def create_random_scraper(self):
        user_agents = self.load_user_agents()
        random_user_agent = random.choice(user_agents)
        scraper = cloudscraper.create_scraper(browser={
            'browser': 'chrome',
            'platform': 'windows',
            'mobile': False,
            'custom': random_user_agent
        })
        return scraper

    # Function to add random delay
    def random_delay(self):
        time.sleep(random.uniform(1, 5))  # Random delay between 1 to 5 seconds

    def get_soup(self, url):
        self.random_delay()  # Add delay before request
        response = self.scraper.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup

    def _real_extract(self, url):
        # Use methods and properties from InfoExtractor as needed
        video_id = self._match_id(url)
        url = f'https://dood.to/e/{video_id}'
        webpage = self.get_soup(url)  # Use the new scraper method

        title = self._html_search_meta(['og:title', 'twitter:title'], str(webpage), default=None)
        thumb = self._html_search_meta(['og:image', 'twitter:image'], str(webpage), default=None)
        token = self._html_search_regex(r'[?&]token=([a-z0-9]+)[&\']', str(webpage), 'token')
        description = self._html_search_meta(
            ['og:description', 'description', 'twitter:description'], str(webpage), default=None)

        # Use urljoin utility from yt_dlp
        base_url = 'https://dood.to'
        pass_md5 = self._html_search_regex(r'(/pass_md5.*?)\'', str(webpage), 'pass_md5')
        pass_md5_url = urljoin(base_url, pass_md5)
        
        # Retrieve the MD5 part of the URL with the scraper
        pass_md5_response = self.scraper.get(pass_md5_url)
        pass_md5_content = pass_md5_response.text

        final_url = ''.join((
            pass_md5_content,
            *(random.choice(string.ascii_letters + string.digits) for _ in range(10)),
            f'?token={token}&expiry={int(time.time() * 1000)}',
        ))

        return {
            'id': video_id,
            'title': title,
            'url': final_url,
            'http_headers': {'referer': url},
            'ext': 'mp4',
            'description': description,
            'thumbnail': thumb,
        }

# Instantiate the class
dood_stream_ie = DoodStreamIE()
