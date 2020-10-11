from datetime import datetime
from collections import Counter
def make_hist_youbi(filename,year):
    dow = ['Sun','Mon','Tue',"Wed","Thu","Fri","Sat"]
    import matplotlib.pyplot as plt
    plt.close()
    with open(filename) as f:
        dates = f.readlines()
    dates = list(map(lambda x:datetime.strptime(x.strip(),"%Y-%m-%d").strftime('%a'),dates))
    plt.title(year)
    plt.ylim([0,4000])
    count_dict = Counter(dates)
    y = [count_dict[dow_]  for dow_ in dow]
    plt.bar(dow,y)
    plt.savefig(f"{year}_day_of_week.pdf")

