from datetime import datetime
from collections import Counter
import matplotlib.pyplot as plt
def make_hist_month(filename,year):
    months = ["Jun","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    with open(filename) as f:
        dates = f.readlines()
    dates = list(map(lambda x:datetime.strptime(x.strip(),"%Y-%m-%d").strftime('%b'),dates))
    plt.title(year)
    plt.ylim([0,4000])
    count_dict = Counter(dates)
    y = [count_dict[month]  for month in months]
    plt.bar(months,y)
    plt.savefig(f"{year}_months.pdf")
