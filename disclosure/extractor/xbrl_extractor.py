import os
import shutil
import zipfile
from glob import glob
from loguru import logger


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

            for xbrl_path in xbrl_path_list:
                os.makedirs(f"{xbrl_save_dir}/{doc_id}/{doc_type}", exist_ok=True)
                # ファイル移動・リネーム
                shutil.move(
                    xbrl_path,
                    f"{xbrl_save_dir}/{doc_id}/{doc_type}/{xbrl_path.split('/')[-1]}",
                )

        # その他のファイルは削除
        for dir_name in ["XBRL", "PublicDoc", "AuditDoc"]:
            xbrl_dir = f"{xbrl_save_dir}/{dir_name}"
            if os.path.exists(xbrl_dir):
                shutil.rmtree(xbrl_dir)
