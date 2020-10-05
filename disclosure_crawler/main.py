import os
import shutil
import zipfile
from collections import defaultdict
from datetime import datetime, timedelta
from glob import glob
from typing import List

import click
from dateutil.relativedelta import relativedelta
from loguru import logger

from disclosure_crawler.crawler.disclosure_file_crawler import DisclosureFileCrawler
from disclosure_crawler.crawler.disclosure_meta_file_crawler import (
    DisclosureMetaFileCrawler,
    MetaRecord,
)


def get_dates(from_day: str, to_day: str) -> List[str]:
    """
    daysの単位は日
    days+1日前から昨日までの日付のリストを作成する
    今日までにしない理由は一日分を取得できない可能性があるため
    """
    format = "%Y-%m-%d"
    from_day_ = datetime.strptime(from_day, format)
    to_day_ = datetime.strptime(to_day, format)
    max_days = 366 * 5
    dates = [
        day_.strftime(format)
        for day in range(max_days)
        if (day_ := from_day_ + timedelta(days=day)) <= to_day_
    ]

    return dates


def crawl_and_unzip_disclosure_each_date_from_metafiles(meta_files, save_dir):
    # 同じ日付ごとに分ける
    date_doc_ids_dict = defaultdict(set)
    for meta_file in meta_files:
        date_doc_ids_dict[meta_file.date].add(meta_file.doc_id)
    logger.info(
        [f"{date}: {len(doc_ids)} files" for date, doc_ids in date_doc_ids_dict.items()]
    )

    # EDINET APIからzipファイルをダウンロード
    for date, doc_ids in date_doc_ids_dict.items():
        logger.info(date)
        # format change
        date_ = datetime.strptime(date, "%Y-%m-%d").strftime("%Y%m%d")

        zip_save_dir = os.path.join(save_dir, "zip", date_)
        os.makedirs(zip_save_dir, exist_ok=True)

        DisclosureFileCrawler(doc_ids, zip_save_dir).run()

        xbrl_save_dir = os.path.join(save_dir, "xbrl_files", date_)
        os.makedirs(xbrl_save_dir, exist_ok=True)

        # 展開してxbrlファイルを抽出
        extract_xbrl(doc_ids, zip_save_dir, xbrl_save_dir)


def extract_xbrl(doc_ids, zip_save_dir, xbrl_save_dir):
    """
    doc_id.zipファイルを展開してdoc_id_AuditDoc.xbrl,doc_id_PublicDoc.xbrlとして保存する
    """
    for doc_id in doc_ids:
        zip_path = f"{zip_save_dir}/{doc_id}.zip"
        if not os.path.exists(zip_path):
            logger.info(f"[no exists] {zip_path}")
            continue

        # zipの展開
        with zipfile.ZipFile(zip_path) as existing_zip:
            existing_zip.extractall(xbrl_save_dir)
        for doc_type in ["AuditDoc", "PublicDoc"]:
            xbrl_path_list = glob(
                f"{xbrl_save_dir}/XBRL/{doc_type}/**/*.xbrl", recursive=True
            )
            xbrl_path_list = (
                glob(f"{xbrl_save_dir}/{doc_type}/**/*.xbrl", recursive=True)
                if xbrl_path_list == []
                else xbrl_path_list
            )
            if xbrl_path_list == []:
                logger.error(f"[no xbrl] {doc_id}")

            for idx, xbrl_path in enumerate(xbrl_path_list):
                # ファイル移動・リネーム
                shutil.move(
                    xbrl_path, f"{xbrl_save_dir}/{doc_id}_{doc_type}_{idx}.xbrl"
                )

        # その他のファイルは削除
        for dir_name in ["XBRL", "PublicDoc", "AuditDoc"]:
            xbrl_dir = f"{xbrl_save_dir}/{dir_name}"
            if os.path.exists(xbrl_dir):
                shutil.rmtree(xbrl_dir)


def is_valid_duration(from_day: str, to_day: str):
    """
    有効な日付でないとエラーを吐く
    """
    # 日付, フォーマットが妥当か,
    from_day_ = datetime.strptime(from_day, "%Y-%m-%d")
    to_day_ = datetime.strptime(to_day, "%Y-%m-%d")

    # fromとtoの順序が正しいか
    if from_day_ > to_day_:
        raise InvlaidDateException(f"{from_day} > {to_day_}")

    # 5年以内のか
    five_years_ago = datetime.today() - relativedelta(years=5)
    if from_day_ < five_years_ago:
        raise InvlaidDateException(f"{from_day_} < 5 yours ago")

    if to_day_ < five_years_ago:
        raise InvlaidDateException(f"{to_day_} < 5 yours ago")

    return True


class InvlaidDateException(Exception):
    pass


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
    type=bool,
    default=False,
    help="Whether to extract the xbrl file (default: False)",
)
def main(from_day, to_day, is_extract):
    # ダウンロードする日付を取得
    is_valid_duration(from_day, to_day)
    dates = get_dates(from_day, to_day)

    # 結果を保存するディレクトリを作成
    meta_file_dir = os.getcwd() + "/output/meta_file"
    os.makedirs(meta_file_dir, exist_ok=True)

    # EDINET APIからメタ情報を取得する(法人番号, 企業名, ファイルコードのtsvファイルで保存する)
    meta_files: List[MetaRecord] = DisclosureMetaFileCrawler(dates, meta_file_dir).run()

    if is_extract == True:
        disclosure_file_dir = os.getcwd() + "/output/disclosure_file"
        crawl_and_unzip_disclosure_each_date_from_metafiles(
            meta_files, disclosure_file_dir
        )


if __name__ == "__main__":
    main()
