from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
from json import loads, dumps

DAYS_PER_MONTH = 30
MONTHS = ["Tishrei", "Kheshvan", "Kislev", "Tevet", "Shvat", "Adar", "Nisan", "Iyar", "Sivan", "Tammuz", "Av", "Elul"]
current_month_index = 0
current_day_of_month = 0


class Day:
    def __init__(self, start, end, day_of_month, month, day_of_week, heights, yom_tov = ""):
        """
        A day in the Aquatic Jewish lunitidal calendar.

        :param start: Start datetime (Gregorian)
        :param end: End datetime (Gregorian)
        :param day_of_month: The day of the aquatic month.
        :param month: The aquatic month.
        :param day_of_week: The day of the aquatic week.
        :param heights: The tidal height data.
        :param yom_tov: Name of yom tov (Default=empty).
        """

        self.start = start
        self.end = end
        self.day_of_month = day_of_month
        self.month = month
        self.day_of_week = day_of_week
        self.heights = heights
        self.yom_tov = yom_tov


def get_start_time():
    for i in range(1, len(heights) - 1):
        if heights[i] > heights[i - 1] and heights[i] > heights[i + 1]:
            return i
    return -1


def get_t1(start_time):
    got_middle_high_tide = False
    for i in range(start_time + 1, len(heights) - 1):
        if heights[i] > heights[i - 1] and heights[i] > heights[i + 1]:
            if got_middle_high_tide:
                return i
            else:
                got_middle_high_tide = True
    return -1


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
    # plt.show()


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
t1 = get_t1(t0)

days = []

done = False
while not done:
    current_day_of_month += 1
    if current_day_of_month > DAYS_PER_MONTH - 1:
        current_day_of_month = 0
        current_month_index += 1
        if current_month_index > len(MONTHS) - 1:
            done = True
    if not done:
        day = Day(t[t0], t[t1], current_day_of_month, MONTHS[current_month_index], "?", heights[t0 : t1])
        days.append(day)
        t0 = t1
print(len(days))

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