import random
import time
import json
import cloudscraper
from bs4 import BeautifulSoup
from yt_dlp.extractor.common import InfoExtractor
from yt_dlp.utils import urljoin, ExtractorError, traverse_obj

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
        super().__init__()
        self.scraper = self.create_random_scraper()

    def load_user_agents(self):
        with open('/content/cloudscraper/cloudscraper/user_agent/browsers.json', 'r') as file:
            data = json.load(file)
            return data['user_agents']['desktop']['windows']['chrome']

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

    def random_delay(self):
        time.sleep(random.uniform(1, 5))

    def get_soup(self, url):
        self.random_delay()
        response = self.scraper.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage_url = f'https://dood.to/e/{video_id}'
        webpage = self.get_soup(webpage_url)

        title = self._html_search_meta(['og:title', 'twitter:title'], str(webpage), default=None)
        thumb = self._html_search_meta(['og:image', 'twitter:image'], str(webpage), default=None)
        token = self._html_search_regex(r'[?&]token=([a-z0-9]+)[&\']', str(webpage), 'token', fatal=False)
        description = self._html_search_meta(
            ['og:description', 'description', 'twitter:description'], str(webpage), default=None)

        if not token:
            raise ExtractorError('Unable to extract token', expected=True)

        pass_md5 = self._html_search_regex(r'(/pass_md5.*?)\'', str(webpage), 'pass_md5')
        pass_md5_url = urljoin('https://dood.to', pass_md5)
        pass_md5_content = self.scraper.get(pass_md5_url).text

        final_url = ''.join((
            pass_md5_content,
            *(random.choice(string.ascii_letters + string.digits) for _ in range(10)),
            f'?token={token}&expiry={int(time.time() * 1000)}',
        ))

        return {
            'id': video_id,
            'title': title,
            'url': final_url,
            'http_headers': {'referer': webpage_url},
            'ext': 'mp4',
            'description': description,
            'thumbnail': thumb,
        }

# Register the custom extractor
yt_dlp.extractor.gen_extractors().append(DoodStreamIE())
