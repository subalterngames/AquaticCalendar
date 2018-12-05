from datetime import datetime, timedelta
from pytides.tide import Tide
import numpy as np
import matplotlib.pyplot as plt


def get_next_low(start_index, prediction):
    for i in range(start_index + 1, len(prediction) - 1):
        if prediction[i] < prediction[i - 1] and prediction[i] < prediction[i + 1]:
            return i
    return -1


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

# Absolute starting time.
t0 = datetime(2018, 9, 8, 19)
hours = np.arange(7 * 24 * 10)
times = Tide._times(t0, hours)

my_tide = Tide.decompose(heights, t)
my_prediction = my_tide.at(times)

day_start = get_next_low(0, my_prediction)
day_end = get_next_low(day_start, my_prediction)

my_prediction = my_prediction[day_start : day_end]
print(my_prediction)
hours = np.arange(len(my_prediction))

plt.plot(hours, my_prediction, label="Pytides")
plt.show()
