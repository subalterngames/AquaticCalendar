from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt


def get_start_time():
    for i in range(1, len(heights) - 1):
        if heights[i] > heights[i - 1] and heights[i] > heights[i + 1]:
            return i
    return -1

def get_next_day(start_time):
    got_middle_high_tide = False
    for i in range(start_time + 1, len(heights) - 1):
        if heights[i] > heights[i - 1] and heights[i] > heights[i + 1]:
            if got_middle_high_tide:
                return i
            else:
                got_middle_high_tide = True
    return -1


def gregorian_to_aquatic(date):
    start_of_calendar = datetime(2018, 9, 9, 3)
    elapsed = timedelta()
    elapsed.total_seconds()
    elapsed = (date - start_of_calendar).total_seconds() / 60.0 / 60.0
    print(elapsed)
    months = ["Tishrei"]

    print(date)


def plot(day):
    ax = plt.axes([0, 0, 1, 1], frameon=False)
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    plt.autoscale(tight=True)

    hours = np.arange(len(day))

    lines = plt.plot(hours, day, label="Pytides")
    plt.setp(lines, linewidth=10)
    plt.tick_params(axis="both", which="both", bottom=False, top=False, left=False, right=False,
                    labelbottom=False, labelleft=False)
    plt.show()


heights = []
t = []
with open('CO-OPS__8443970__hr.csv', 'rt') as f:
    for i, line in enumerate(f):
        if i == 0:
            continue
        line = line.strip()
        date_string = line.split(',')[:2][0]
        t.append(datetime.strptime(date_string, "%Y-%m-%d %H:%M"))
        heights.append(float(line.split(',')[1]))

heights = np.array(heights)
t = np.array(t)

t0 = get_start_time()
t1 = get_next_day(t0)

plot(heights[t0:t1])
print(t[t0])

"""
# Absolute starting time.
t0 = datetime(2018, 9, 8, 19)

times = Tide._times(t0, hours)

my_tide = Tide.decompose(heights, t)
my_prediction = my_tide.at(times)

day_start = get_next_low(0, my_prediction)
day_end = get_next_low(day_start, my_prediction)

my_prediction = my_prediction[day_start : day_end]
print(my_prediction)
hours = np.arange(len(my_prediction))

ax = plt.axes([0, 0, 1, 1], frameon=False)
ax.get_xaxis().set_visible(False)
ax.get_yaxis().set_visible(False)
plt.autoscale(tight=True)

lines = plt.plot(hours, my_prediction, label="Pytides")
plt.setp(lines, linewidth=10)
plt.tick_params(axis="both", which="both", bottom=False, top=False, left=False, right=False,
                labelbottom=False, labelleft=False)
plt.show()
"""