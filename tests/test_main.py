from disclosure_crawler.main import is_valid_duration, get_dates, InvlaidDateException
from dateutil.relativedelta import relativedelta
import pytest
from datetime import datetime, timedelta


def test_is_valid_duration():
    # 正しい日付指定
    from_date = (datetime.today() - timedelta(days=5)).strftime("%Y-%m-%d")
    to_date = datetime.today().strftime("%Y-%m-%d")
    assert is_valid_duration(from_date, to_date) == True

    # 日付, フォーマットが妥当か
    from_date = (datetime.today() - timedelta(days=1)).strftime("%Y/%m/%d")
    to_date = datetime.today().strftime("%Y/%m/%d")
    with pytest.raises(ValueError):
        is_valid_duration(from_date, to_date)

    # fromとtoの順序が逆
    from_date = datetime.today().strftime("%Y-%m-%d")
    to_date = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    with pytest.raises(InvlaidDateException):
        is_valid_duration(from_date, to_date)

    # 5年以上古い日付
    from_date = (datetime.today() - relativedelta(years=6)).strftime("%Y-%m-%d")
    to_date = datetime.today().strftime("%Y-%m-%d")
    with pytest.raises(InvlaidDateException):
        is_valid_duration(from_date, to_date)


def test_get_dates():
    from_day = "2020-10-01"
    to_day = "2020-10-05"
    expected = ["2020-10-01", "2020-10-02", "2020-10-03", "2020-10-04", "2020-10-05"]
    assert expected == get_dates(from_day, to_day)

    from_day = "2020-10-01"
    to_day = "2020-10-01"
    expected = ["2020-10-01"]
    assert expected == get_dates(from_day, to_day)
