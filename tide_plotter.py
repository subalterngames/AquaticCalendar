from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import decimal
dec = decimal.Decimal


MONTHS = ["Tishrei", "Kheshvan", "Kislev", "Tevet", "Shvat", "Adar", "Nisan", "Iyar", "Sivan", "Tammuz", "Av", "Elul"]
DAYS_OF_WEEK = ["Dag", "Gal", "Khof", "Sa'ar", "Shakhaf", "Melakh", "Shabbat"]
MOON_PHASES = [r"\CIRCLE", r"\LEFTcircle", r"\Circle", "\RIGHTcircle", r""]
current_month_index = 0
current_day_of_month = -1
current_day_of_week = 0

tex = r"\documentclass[11pt,letterpaper,landscape]{scrbook}\usepackage{cjhebrew}\usepackage{tabularx}\usepackage[letterpaper,bindingoffset=0.2in,left=1in,right=1in,top=.5in,bottom=.5in,footskip=.25in,marginparwidth=5em]{geometry}\usepackage{marginnote}\usepackage{graphicx}\usepackage{wasysym}\usepackage{sectsty}\usepackage{xcolor}\definecolor{hcolor}{HTML}{D3230C}\newcommand{\red}[1]{\textcolor{hcolor}{#1}}\setkomafont{disposition}{\bfseries}\newcommand\Chapter[2]{\chapter[\normalfont#1:{\itshape#2}]{#1\\[1ex]\Large\normalfont#2}}\makeatletter\newcommand{\alephbet}[1]{\c@alephbet{#1}}\newcommand{\c@alephbet}[1]{{\ifcase\number\value{#1}\or\<'>\or\<b>\or\<g>\or\<d>\or\<h>\or\<w>\or\<z>\or\<.h>\or\<.t>\or\<y>\or\<k|>\or\<l>\or\<m|>\or\<n|>\o\<N>\or\<s>\or\<`>\or\<p|>\or\<P>\or\<.s>\or\<q>\or\<r>\or\</s>\or\<t>\fi}}\renewcommand{\partname}{}\renewcommand\thepart{\alephbet{part}}\renewcommand\thechapter{\alephbet{chapter}}\allsectionsfont{\centering}\newcolumntype{Y}{>{\centering\arraybackslash}X}\begin{document}"
MONTH_TEMPLATE = r"\chapter*{$MONTH}\noindent\begin{tabularx}{\textwidth}{YYYYYYY}"

CELL_TEMPLATE = r"{\huge\textbf{$DAY_OF_MONTH} $MOON_PHASE}\newline {\tiny{\textit{$GREGORIAN_TIME}}}\newline\scriptsize{\textit{YOMTOV}}\newline TIDEIMAGE"


def get_lunar_phase(time_index):
    diff = t[time_index] - datetime(2001, 1, 1)
    days = dec(diff.days) + (dec(diff.seconds) / dec(86400))
    lunations = dec("0.20439731") + (days * dec("0.03386319269"))
    return lunations % dec(1)


def get_new_month():
    """
    Returns the header for the next month.
    """
    month = MONTH_TEMPLATE
    month = month.replace("$MONTH", MONTHS[current_month_index])
    for day_of_week, i in zip(DAYS_OF_WEEK, range(len(DAYS_OF_WEEK))):
        month += r"\huge " + day_of_week
        if i < len(DAYS_OF_WEEK) - 1:
            month += "&"
        else:
            month += r"\\"
    month += r"\end{tabularx}\\\noindent\begin{tabularx}{\textwidth}{|X|X|X|X|X|X|X|}\hline"
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
    ax = plt.axes([0, 0, 1, 1], frameon=False)
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    plt.autoscale(tight=True)

    hours = np.arange(len(day))

    lines = plt.plot(hours, day)
    plt.setp(lines, linewidth=10)
    plt.tick_params(axis="both", which="both", bottom=False, top=False, left=False, right=False,
                    labelbottom=False, labelleft=False)
    # plt.show()

def get_end_month():
    end_of_table = ""
    for i in range(6 - current_day_of_week):
        end_of_table += r"&"
    end_of_table += r"\\\hline\end{tabularx}"
    return end_of_table

# Parse the csv file.
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

# Get the first day.
t0 = get_start_time()

done = False
first_month = True
while not done:
    current_day_of_month += 1

    t1 = get_t1(t0)

    moon_phase_t0 = get_lunar_phase(t0)
    moon_phase_t1 = get_lunar_phase(t1)

    # New moon
    if moon_phase_t0 > 0.75 and moon_phase_t1 < 0.125:
        moon_phase_index = 0
        if current_month_index + 1 >= 2:
            done = True
            tex += get_end_month()
        else:
            if first_month:
                first_month = False
            else:
                tex += get_end_month() + r"\\"
            tex += get_new_month()
            current_month_index += 1
    elif moon_phase_t0 < 0.25 and moon_phase_t1 > 0.25:
        moon_phase_index = 1
    elif moon_phase_t0 < 0.5 and moon_phase_t1 > 0.5:
        moon_phase_index = 2
    elif moon_phase_t0 < 0.75 and moon_phase_t1 > 0.75:
        moon_phase_index = 3
    else:
        moon_phase_index = 4

    if done:
        continue

    calendar_cell = CELL_TEMPLATE
    calendar_cell = calendar_cell.replace("$DAY_OF_MONTH", str(current_day_of_month))
    calendar_cell = calendar_cell.replace("$GREGORIAN_TIME", t[t0].strftime("%m.%d.%y %H:%M"))
    calendar_cell = calendar_cell.replace("$MOON_PHASE", MOON_PHASES[moon_phase_index])
    # TODO yom tov
    # TODO tide image

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