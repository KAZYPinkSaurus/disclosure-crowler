from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import List


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
