# disclosure-crowler
EDINET APIから任意の期間の有価証券報告書を禁止事項に反しないように優しく取得する


# Install requirements via poetry
```shell
poetry install
```

# How to use
```shell 
# download disclosures which is submitted from 2020/01/01 to today.
poetry run python -m disclosure.main -f 2020-01-01

# download disclosures which is submitted from 2020/01/01 to 2020/01/03 and extract zip.
poetry run python -m disclosure.main -f 2020-01-01 -t 2020-01-03 -x
```

# Options
```shell
Usage: main.py [OPTIONS]

Options:
  -f, --from TEXT     YYYY-MM-DD  [required]
  -t, --to TEXT       YYYY-MM-DD (default: today)
  -x, --xbrl_extract  Whether to extract the xbrl file
  --help              Show this message and exit.
```
