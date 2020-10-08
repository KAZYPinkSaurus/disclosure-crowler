import os
from datetime import datetime
from typing import List

import click

from disclosure.crawler.each_date_file_cralwer import (
    crawl_disclosure_each_date_from_metafile,
)
from disclosure.crawler.meta_file_crawler import DisclosureMetaFileCrawler, MetaRecord
from disclosure.util.date_manager import get_dates, is_valid_duration


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
