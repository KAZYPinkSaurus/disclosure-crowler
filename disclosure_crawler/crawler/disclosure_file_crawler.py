from disclosure_crawler.crawler.disclosure_meta_file_crawler import (
    DisclosureMetaFileCrawler,
    MetaRecord,
)
import requests
import csv
from loguru import logger
import os
from time import sleep
from typing import List

SLEEPTIME = 1

# TODO:Retry


class DisclosureFileCrawler:
    url = "https://disclosure.edinet-fsa.go.jp/api/v1/documents/"
    params = {"type": 1}

    def __init__(self, doc_ids: List[str], save_dir):
        self.save_dir = save_dir
        self.doc_ids = doc_ids

    def run(self):
        for doc_id in self.doc_ids:
            is_done = self._save_disclosure_file(doc_id)
            if is_done == True:
                logger.info(f"[save ok] {doc_id}")
            else:
                logger.warn(
                    f"[save ng] requests status code is {res.status_code}, {doc_id}"
                )

    def _save_disclosure_file(self, doc_id):
        res = requests.get(self.url + doc_id, params=self.params)

        if res.status_code != requests.status_codes.codes.ok:
            return False

        file_name = os.path.join(self.save_dir, f"{doc_id}.zip")
        with open(file_name, "wb") as f:
            for chunk in res.iter_content(chunk_size=1024):
                f.write(chunk)
        return True
