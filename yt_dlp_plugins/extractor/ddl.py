import random
import time
import json
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import yt_dlp
from yt_dlp.extractor.common import InfoExtractor
from yt_dlp.utils import urljoin, ExtractorError, traverse_obj
import google_colab_selenium as gs

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
        self.driver = self.setup_selenium()

    def setup_selenium(self):
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36']
        
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--incognito")
        options.add_argument(f'--user-agent={random.choice(user_agents)}')
        driver = gs.Chrome(options=options)
        return driver

    def get_page_content(self, url, request_interval=2, page_load_delay=2):
        self.driver.get(url)
        time.sleep(request_interval)
        html_content = self.driver.page_source
        time.sleep(page_load_delay)
        return html_content

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage_url = f'https://dood.to/e/{video_id}'
        webpage = self.get_page_content(webpage_url)
        soup = BeautifulSoup(webpage, 'html.parser')

        title = self._html_search_meta(['og:title', 'twitter:title'], str(soup), default=None)
        thumb = self._html_search_meta(['og:image', 'twitter:image'], str(soup), default=None)
        token = self._html_search_regex(r'[?&]token=([a-z0-9]+)[&\']', str(soup), 'token', fatal=False)
        description = self._html_search_meta(
            ['og:description', 'description', 'twitter:description'], str(soup), default=None)

        if not token:
            raise ExtractorError('Unable to extract token', expected=True)

        pass_md5 = self._html_search_regex(r'(/pass_md5.*?)\'', str(soup), 'pass_md5')
        pass_md5_url = urljoin('https://dood.to', pass_md5)
        pass_md5_content = self.driver.get(pass_md5_url).text

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
