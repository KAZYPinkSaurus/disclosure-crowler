import json
import re
import os
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional
from loguru import logger
import requests

requests.urllib3.disable_warnings()

# TODO:日付ごとにディレクトリを分ける
# TODO:むずかしいなぁ受け渡し


class StatusCode(Enum):
    ok = "200"


class DocTypeCode(Enum):
    disclosure = "120"


@dataclass(frozen=True)
class MetaRecord:
    date: Optional[str] = None
    doc_id: Optional[str] = None
    edint_code: Optional[str] = None
    corporate_number: Optional[str] = None
    company_name: Optional[str] = None

    @property
    def record(self):
        return "\t".join(map(str, list(vars(self).values())))

    @property
    def header(self):
        return "\t".join(map(str, list(vars(self).keys())))


class DisclosureMetaFileCrawler:
    # API
    url = "https://disclosure.edinet-fsa.go.jp/api/v1/documents.json"

    def __init__(self, dates, save_dir):
        self.dates = dates
        self.output_tsv = os.path.join(save_dir, "meta_file.tsv")

    def run(self):
        meta_files = [meta_file for meta_file in self._get_meta_files()]
        logger.info(f"meta file size: {len(meta_files)}")
        self._write_meta_files(meta_files)
        return meta_files

    def _get_meta_files(self) -> Optional[MetaRecord]:
        for params in self._generate_params(self.dates):
            res = requests.get(self.url, params=params, verify=False)
            if res.status_code != requests.status_codes.codes.ok:
                logger.warning(
                    f"[skip] status code:{res.status_code}, params: {params}"
                )
                yield None
            yield from self.generate_metarecord_from_response(res.text)

    def generate_metarecord_from_response(self, text: str):
        response_dict = json.loads(text)
        if (metadata := response_dict.get("metadata")) is None:
            logger.warning(f'[skip] not found "metadata" {text}')
            return None
        if (status := metadata.get("status")) != StatusCode.ok.value:
            logger.warning(f'[skip] not found "status" {text}')
            return None
        if (parameter := metadata.get("parameter")) is None:
            logger.warning(f'[skip] not found "parameter" {text}')
            return None
        if (date := parameter.get("date")) is None:
            logger.warning(f'[skip] not found "date" {text}')
            return None
        if (results := response_dict.get("results")) is None:
            logger.warning(f'[skip] not found "results" {text}')
            return None

        for result in results:
            if result["docTypeCode"] != DocTypeCode.disclosure.value:
                continue
            yield MetaRecord(
                date,
                result["docID"],
                result["edinetCode"],
                result["JCN"],
                re.sub("\s", "", result["filerName"]),
            )

    def _generate_params(self, dates: List[str]):
        for date in dates:
            logger.info(date)
            yield {"date": date, "type": 2}

    def _write_meta_files(self, meta_files: List[MetaRecord], header=True):

        with open(self.output_tsv, mode="w") as f:
            if header == True:
                f.write(MetaRecord().header + "\n")

            for meta_file in meta_files:
                f.write(meta_file.record + "\n")
