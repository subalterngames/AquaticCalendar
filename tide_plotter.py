from pathlib import Path
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
from dateutil import tz
import decimal
dec = decimal.Decimal


MONTHS = ["Tishrei", "Kheshvan", "Kislev", "Tevet", "Shvat", "Adar", "Nisan", "Iyar", "Sivan", "Tammuz", "Av", "Elul"]
DAYS_OF_WEEK = ["Dag", "Gal", "Khof", "Sa'ar", "Shakhaf", "Melakh", "Shabbat"]
MOON_PHASES = [r"\CIRCLE", r"\LEFTcircle", r"\Circle", "\RIGHTcircle", r""]
current_month_index = -1
current_day_of_month = -1
current_day_of_week = 0

image_counter = 0

# Begin building the document with the preamble.
tex = r"\documentclass[11pt,letterpaper,landscape,openany]{scrbook}\renewcommand{\familydefault}{\sfdefault}\usepackage{cjhebrew}\usepackage{tabularx}\usepackage[letterpaper,bindingoffset=0.2in,left=1in,right=1in,top=.5in,bottom=.5in,footskip=.25in,marginparwidth=5em]{geometry}\usepackage{marginnote}\usepackage{graphicx}\usepackage{wasysym}\usepackage{sectsty}\usepackage{xcolor}\definecolor{hcolor}{HTML}{D3230C}\newcommand{\red}[1]{\textcolor{hcolor}{#1}}\setkomafont{disposition}{\bfseries}\newcommand\Chapter[2]{\chapter[\normalfont#1:{\itshape#2}]{#1\\[1ex]\Large\normalfont#2}}\makeatletter\newcommand{\alephbet}[1]{\c@alephbet{#1}}\newcommand{\c@alephbet}[1]{{\ifcase\number\value{#1}\or\<'>\or\<b>\or\<g>\or\<d>\or\<h>\or\<w>\or\<z>\or\<.h>\or\<.t>\or\<y>\or\<k|>\or\<l>\or\<m|>\or\<n|>\o\<N>\or\<s>\or\<`>\or\<p|>\or\<P>\or\<.s>\or\<q>\or\<r>\or\</s>\or\<t>\fi}}\renewcommand{\partname}{}\renewcommand\thepart{\alephbet{part}}\renewcommand\thechapter{\alephbet{chapter}}\allsectionsfont{\centering}\newcolumntype{Y}{>{\centering\arraybackslash}X}\begin{document}"

# Append the introduction.
with open("intro.txt", "rt") as f:
    tex += f.read()

MONTH_TEMPLATE = r"\chapter*{$MONTH}\noindent\begin{tabularx}{\textwidth}{YYYYYYY}"

CELL_TEMPLATE = r"{\huge\textbf{$DAY_OF_MONTH} $MOON_PHASE}\newline {\tiny{$GREGORIAN_TIME}}\newline\scriptsize{\textbf{$YOM_TOV}}\newline $TIDE_IMAGE"

plot_directory = Path("plots")
if not plot_directory.exists():
    plot_directory.mkdir()

yom_tov = []
with open("yom_tov.csv", "rt") as f:
    for line in f.readlines():
        cols = line.strip().split('\t')
        if len(cols) == 3:
            note = ""
        else:
            note = cols[3]
        yom_tov.append({"month": cols[0], "day": int(cols[1]), "yom_tov": cols[2], "note": note})


def is_yom_tov():
    """
    Returns true if the current day is a yom tov.
    """

    for y in yom_tov:
        if y["month"] == MONTHS[current_month_index] and y["day"] - 1 == current_day_of_month:
            return y["yom_tov"], y["note"], True
    return "", "", False


def get_lunar_phase(time_index):
    diff = t[time_index] - datetime(2001, 1, 1)
    days = dec(diff.days) + (dec(diff.seconds) / dec(86400))
    lunations = dec("0.20439731") + (days * dec("0.03386319269"))
    return lunations % dec(1)


def get_new_month():
    """
    Returns the header for the next month.
    """
    global current_day_of_month
    current_day_of_month = 0
    global current_month_index
    current_month_index += 1
    month = MONTH_TEMPLATE
    month = month.replace("$MONTH", MONTHS[current_month_index])
    for day_of_week, i in zip(DAYS_OF_WEEK, range(len(DAYS_OF_WEEK))):
        month += r"\normalsize " + day_of_week
        if i < len(DAYS_OF_WEEK) - 1:
            month += "&"
        else:
            month += r"\\"
    month += r"\end{tabularx}\\\noindent\begin{tabularx}{\textwidth}{|X|X|X|X|X|X|X|}\hline"
    for i in range(current_day_of_week):
        month += "&"
    return month


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
    """
    Create a tidal chart of the day.
    :param day: The day, as represented by an array of heights per hour.
    """

    ax = plt.axes([0, 0, 1, 1], frameon=False)
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    plt.autoscale(tight=True)

    hours = np.arange(len(day))
    # Plot invisible lines to keep the size of the chart consistent.
    plt.plot(min_max_range, min_max_heights, color="white")
    # Plot the heights.
    lines = plt.plot(hours, day, color="#cfe0e8")
    plt.setp(lines, linewidth=20)

    # Save the image.
    plt.tick_params(axis="both", which="both", bottom=False, top=False, left=False, right=False,
                    labelbottom=False, labelleft=False)
    # Save the image.
    global image_counter
    plt.savefig(plot_directory.joinpath(str(image_counter) + ".png"))
    plt.clf()
    image_counter += 1

def get_end_month():
    end_of_table = ""
    for i in range(6 - current_day_of_week):
        end_of_table += r"&"
    end_of_table += r"\\\hline\end{tabularx}"
    return end_of_table

# Parse the csv file.
heights = []
t = []
with open('tide_data/boston.csv', 'rt') as f:
    for i, line in enumerate(f):
        if i == 0:
            continue
        line = line.strip().split(',')
        date_string = line[0] + " " + line[1]
        t.append(datetime.strptime(date_string, "%Y/%m/%d %H:%M:%S %p"))
        heights.append(float(line[2]))

# Use the max and min heights to plot consistenty sized charts.
min_max_heights = np.array([min(heights), max(heights)])
min_max_range = np.arange(2)

heights = np.array(heights)
t = np.array(t)

# Get the first day.
t0 = get_start_time()

to_zone = tz.gettz('America/New_York')

done = False
first_month = True
while not done:
    # Get the ending hour of the day.
    t1 = get_t1(t0)

    # Increment the day of month.
    current_day_of_month += 1

    # Get the lunar phase at the start and end of the day.
    moon_phase_t0 = get_lunar_phase(t0)
    moon_phase_t1 = get_lunar_phase(t1)

    # Get the LaTeX symbol for the elapsed phase, if any.
    # If the phase wrapped around, it is a new month.
    if moon_phase_t0 > 0.75 and moon_phase_t1 < 0.125:
        # Start the next month.
        moon_phase_index = 0
        #if current_month_index + 1 >= len(MONTHS):
        if current_month_index + 1 >= 1:
            done = True
            tex += get_end_month()
        else:
            if first_month:
                first_month = False
            else:
                tex += get_end_month() + r"\\"
            tex += get_new_month()
    elif moon_phase_t0 < 0.25 and moon_phase_t1 > 0.25:
        moon_phase_index = 1
    elif moon_phase_t0 < 0.5 and moon_phase_t1 > 0.5:
        moon_phase_index = 2
    elif moon_phase_t0 < 0.75 and moon_phase_t1 > 0.75:
        moon_phase_index = 3
    # Do not show a lunar symbol.
    else:
        moon_phase_index = 4

    if done:
        continue

    # Create a "cell" in the calendar.
    calendar_cell = CELL_TEMPLATE

    calendar_day_of_month = str(current_day_of_month + 1)
    # Add a bit of vertical padding on the top.
    if current_day_of_week == 0:
        calendar_day_of_month += r"\rule{0pt}{2ex}"

    # Add the day of month.
    calendar_cell = calendar_cell.replace("$DAY_OF_MONTH", calendar_day_of_month)

    # Convert the printed time to the current time zone.
    d = t[t0]
    d = d.replace(tzinfo=to_zone)
    # Add the current time in the Gregorian (secular) calendar.
    calendar_cell = calendar_cell.replace("$GREGORIAN_TIME", d.strftime("%m.%d.%y %H:%M %p"))

    # Add the moon phase, if any.
    calendar_cell = calendar_cell.replace("$MOON_PHASE", r" \hfill " + MOON_PHASES[moon_phase_index])

    # Add the yom tov reminder, if any.
    y, y_notes, is_y = is_yom_tov()
    if is_y:
        if y_notes != "":
            # Remove the word "begins" from the margin note.
            if y.endswith("begins"):
                y_name = y.split(" ")[0]
            else:
                y_name = y
            # Add a margin note about the yom tov, if any.
            y += r"\marginnote{\tiny{\textbf{" + y_name + r"}\newline\textit{" + y_notes + r"}}}"
        calendar_cell = calendar_cell.replace("$YOM_TOV", y)
    else:
        calendar_cell = calendar_cell.replace("$YOM_TOV", "")

    # Add the image.
    calendar_cell = calendar_cell.replace("$TIDE_IMAGE", r"\includegraphics[width=\linewidth,keepaspectratio=true]{plots/" + str(image_counter) + r".png}")
    image_counter += 1
    # Create the image.
    # np.array(heights[t0:t1]))

    # TODO a pretty picture of the ocean per month.
    # TODO title page.
    # TODO blue fonts.
    # TODO correct size.

    tex += calendar_cell

    current_day_of_week += 1
    if current_day_of_week >= len(DAYS_OF_WEEK):
        tex += r"\\\hline "
        current_day_of_week = 0
    else:
        tex += r"&"
    t0 = t1
tex += r"\end{document}"
print(tex)

with open("calendar.tex", "wt") as f:
    f.write(tex)

print("Done!")