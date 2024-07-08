import json
import logging
import random as rand
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup
from utils.paths import Resource


@dataclass
class BooruScheme:
    booru_name: str
    booru_search_url: str = "https://{booru_name}.booru.org/index.php?page=post&s=list&tags="
    preview_thumb_id_start: str = "thumbnails//"
    preview_thumb_id_end: str = "/"
    preview_thumb_name_start: str = "thumbnail_"
    preview_thumb_name_end: str = "."
    score_start: str = "score:"
    score_end: str = " "
    raw_image_url: str = "https://img.booru.org/{booru}//images/{code_actual}/"


# booru handling class
class BooruDownloader:
    def __init__(self, booru: str, tags: list[str] = None):
        self.extension_list: list[str] = ["jpg", "jpeg", "png", "gif"]

        self.exception_list: dict[str, BooruScheme] = {
            "rule34": BooruScheme(
                "rule34",
                "https://www.rule34.xxx/index.php?page=post&s=list&tags=",
                "/thumbnails/",
                "/",
                "thumbnail_",
                ".",
                "score:",
                " ",
                "https://us.rule34.xxx//images/{code_actual}/",
            )
        }

        self.booru = booru
        self.tags = "+".join(tags) if tags is not None else "all"
        logging.info(f"tags={self.tags}")
        self.post_per_page = 0
        self.page_count = 0
        self.booru_scheme = BooruScheme(self.booru) if self.booru not in self.exception_list.keys() else self.exception_list.get(self.booru)
        self.max_page = int(self.get_page_count())

    def download(self, page_start: int = 0, page_end: int = 1, min_score: int = None) -> None:
        self._page_start = max(page_start, 0)
        self._page_start = min(self._page_start, self.page_count)
        self._page_end = min(page_end, self.max_page + 1) if page_end >= self._page_start else self._page_start + 1

        for page_index in range(self._page_start, self._page_end):
            self._page_url = f"{self.booru_scheme.booru_search_url.format(booru_name=self.booru)}{self.tags}&pid={page_index*self.post_per_page}"
            logging.info(f"downloadpageurl={self._page_url}")
            self._html = requests.get(self._page_url).text
            self._soup = BeautifulSoup(self._html, "html.parser")

            for image in self._soup.find_all("img"):
                try:
                    self._src: str = image.get("src")
                    self._code_actual = int(
                        self.pick_value(self._src, f"{self.booru_scheme.preview_thumb_id_start}", f"{self.booru_scheme.preview_thumb_id_end}")
                    )
                    self._file_name = self.pick_value(self._src, f"{self.booru_scheme.preview_thumb_name_start}", f"{self.booru_scheme.preview_thumb_name_end}")

                    self._title: str = image.get("title")
                    self._start = int(self._title.index(f"{self.booru_scheme.score_start}") + len(self.booru_scheme.score_start))
                    self._end = self._title.index(f"{self.booru_scheme.score_end}", self._start)
                    self._score = int(self._title[self._start : self._end])

                    if min_score is not None and self._score < min_score:
                        print(f"(score {self._score} too low) skipped {self._src}")
                        continue
                except Exception as e:
                    print(f"skipped: {e}")
                    continue

                for extension in self.extension_list:
                    try:
                        self._file_name_full = f"{self._file_name}.{extension}"
                        self._full_url = f"{self.booru_scheme.raw_image_url.format(booru=self.booru, code_actual=self._code_actual)}{self._file_name_full}"
                        direct_download(self._full_url)
                        break
                    except Exception:
                        continue

    def download_random(self, min_score: int = None) -> None:
        self._selected_page = rand.randint(0, self.max_page)
        self.download(self._selected_page, min_score=min_score)

    def download_all(self, min_score: int = None) -> None:
        for page in range(0, self.max_page):
            self.download(page, min_score=min_score)

    def get_page_count(self) -> int:
        self._href_core = self.booru_scheme.booru_search_url.format(booru_name=self.booru).split("?")[0]
        print(f"href_core={self._href_core}")
        self._home_url = f"{self._href_core}?page=post&s=list&tags={self.tags}"
        print(self._home_url)
        self._html = requests.get(self._home_url).text
        self._soup = BeautifulSoup(self._html, "html.parser")
        for a in self._soup.find_all("a"):
            if a.getText() == "2" and self.post_per_page == 0:
                self.post_per_page = int(a.get("href").split("=")[-1])
            if a.get("alt") == "last page":
                self._final_link = f'{self._href_core}{a.get("href")}'
                print(f"last alt={self._final_link}")
                return int(self._final_link[(self._final_link.index("&pid=") + len("&pid=")) :]) / self.post_per_page + 1
        return 0

    def pick_value(self, text: str, start_text: str, end_text: str) -> str:
        start_index = text.index(start_text) + len(start_text)
        end_index = text.index(end_text, start_index)
        return text[start_index:end_index]


def direct_download(url: str) -> None:
    r = requests.get(url)
    if r.status_code == 404:
        raise Exception("Response 404")
    img_data = r.content
    file_name = url.split("/")[-1]
    with open(Resource.IMAGE / file_name, "wb") as handler:
        handler.write(img_data)


# downloads all images listed in webresource.json in resources
def download_web_resources():
    try:
        with open(Resource.WEB_RESOURCE) as op:
            js = json.loads(op.read())
            ls = js["weblist"]
            for link in ls:
                direct_download(link)
    except Exception as e:
        print(e)
