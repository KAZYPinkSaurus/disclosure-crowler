import os
import time
import shutil
import zipfile
from collections import defaultdict
from datetime import datetime
from glob import glob
from typing import List

import click
from loguru import logger

from disclosure.crawler.file_crawler import DisclosureFileCrawler
from disclosure.crawler.meta_file_crawler import (
    DisclosureMetaFileCrawler,
    MetaRecord,
)
from disclosure.extractor.xbrl_extractor import extract_xbrl
from disclosure.util.date_manager import get_dates, is_valid_duration


SLEEP_TIME = 1


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


@click.command()
@click.option("-f", "--from", "from_day", required=True, type=str, help="YYYY-MM-DD")
@click.option(
    "-t",
    "--to",
    "to_day",
    type=str,
    default=datetime.now().strftime("%Y-%m-%d"),
    help=f"YYYY-MM-DD (default: {datetime.now().strftime('%Y-%m-%d')})",
)
@click.option(
    "-x",
    "--xbrl_extract",
    "is_extract",
    is_flag=True,
    help="Whether to extract the xbrl file",
)
def main(from_day, to_day, is_extract):
    # ダウンロードする日付を取得
    is_valid_duration(from_day, to_day)
    dates = get_dates(from_day, to_day)

    # 結果を保存するディレクトリを作成
    meta_file_dir = os.getcwd() + "/output/meta_file"
    os.makedirs(meta_file_dir, exist_ok=True)

    # EDINET APIからメタ情報を取得する(法人番号, 企業名, ファイルコードのtsvファイルで保存する)
    meta_file: List[MetaRecord] = DisclosureMetaFileCrawler(dates, meta_file_dir).run()

    disclosure_file_dir = os.getcwd() + "/output/disclosure_file"
    crawl_disclosure_each_date_from_metafile(meta_file, disclosure_file_dir, is_extract)


if __name__ == "__main__":
    main()
