import os
import shutil
import time
import zipfile
from collections import defaultdict
from datetime import datetime

from loguru import logger

from disclosure.config.config import SLEEP_TIME
from disclosure.crawler.file_crawler import DisclosureFileCrawler
from disclosure.extractor.xbrl_extractor import extract_xbrl


def crawl_disclosure_each_date_from_metafile(meta_file, save_dir, is_extract):
    # 同じ日付ごとに分ける
    date_doc_ids_dict = defaultdict(set)
    for meta_record in meta_file:
        date_doc_ids_dict[meta_record.date].add(meta_record.doc_id)
    logger.info(
        [f"{date}: {len(doc_ids)} files" for date, doc_ids in date_doc_ids_dict.items()]
    )

    # EDINET APIからzipファイルをダウンロード
    for date, doc_ids in date_doc_ids_dict.items():
        time.sleep(SLEEP_TIME)
        logger.info(date)
        # format change
        date_ = datetime.strptime(date, "%Y-%m-%d").strftime("%Y%m%d")

        zip_save_dir = os.path.join(save_dir, "zip", date_)
        os.makedirs(zip_save_dir, exist_ok=True)

        DisclosureFileCrawler(doc_ids, zip_save_dir).run()

        if is_extract == False:
            continue

        xbrl_save_dir = os.path.join(save_dir, "xbrl_files", date_)
        os.makedirs(xbrl_save_dir, exist_ok=True)

        # 展開してxbrlファイルを抽出
        extract_xbrl(doc_ids, zip_save_dir, xbrl_save_dir)
