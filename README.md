# disclosure-crowler
EDINET APIから任意の期間の有価証券報告書を禁止事項に反しないように優しく取得する


# Install requirements via poetry
```shell
poetry install
```

# how to use
```shell 
# download disclosures which is submitted from 2020/01/01 to 2020/01/03.
poetry run python disclosure_crawler.mian -f 2020-01-01 -t 2020-01-03
```

