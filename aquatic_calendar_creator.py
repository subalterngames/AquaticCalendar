from os import devnull
import pkg_resources
from subprocess import call, check_output, CalledProcessError
from platform import system
# Install missing Python modules.
for package in ['requests', 'numpy', 'matplotlib', 'pylunar', 'python-dateutil', 'pyluach']:
    try:
        pkg_resources.get_distribution(package)
    except pkg_resources.DistributionNotFound:
        if system() == "Windows":
            call(["pip3", "install", package, "--user"])
        else:
            call(["sudo", "pip3", "install", package])
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from dateutil.parser import parse
from dateutil import tz
from os import listdir
from argparse import ArgumentParser
from requests import get
import pylunar
import re
from pyluach import dates


# Parse arguments.
parser = ArgumentParser()
parser.add_argument("-s", type=str, default="8443970", help="Tidal station ID")
args = parser.parse_args()

today_he = dates.HebrewDate.today()
# Get the Hebrew year.
year_he = today_he.year
# Get the secular year.
year_gr = today_he.to_greg().year
# Get the start and end day.
rosh_hashana = dates.HebrewDate(year_he, 7, 1)
start_day = rosh_hashana.to_greg()
end_day = dates.HebrewDate(year_he + 1, 6, 29).to_greg()

start_day = str(start_day).split(" ")[0].replace("-", "")
end_day = str(end_day).split(" ")[0].replace("-", "")

# Get the tidal data.
url = f"https://opendap.co-ops.nos.noaa.gov/axis/webservices/predictions/response.jsp?stationId={args.s}&" \
    f"beginDate={start_day}&endDate={end_day}&datum=MLLW&unit=0&timeZone=0&dataInterval=60&format=text&Submit=Submit"
resp = get(url).content.decode("utf-8")

print(f"Got tidal data for station {args.s}")
# Get the longitude and latitude.
latitude = re.search(r"\s+Latitude\s+:\s+(.*)", resp).group(1)
latitude = (int(latitude.split(".")[0]), int(latitude[-4:]), int(latitude[-2:]))
longitude = re.search(r"\s+Longitude\s+:\s+(.*)", resp).group(1)
longitude = (int(longitude.split(".")[0]), int(longitude[-4:]), int(longitude[-2:]))
# Load the lunar data.
mi = pylunar.MoonInfo(latitude, longitude)
mi_start = (int(start_day[:4]), int(start_day[4:6]), int(start_day[6:8]), 0, 0, 0)
mi.update(mi_start)
print("Got the lunar data.")

tidal_data = resp.split("<pre>")[-1].replace("</pre>", "")

# The months of the Aquatic Jewish calendar.
MONTHS = ["Tishrei", "Kheshvan", "Kislev", "Tevet", "Shvat", "Adar", "Nisan", "Iyar", "Sivan", "Tammuz", "Av", "Elul"]
# The days of the Aquatic Jewish week.
DAYS_OF_WEEK = ["Dag", "Gal", "Khof", "Zerem", "Ruakh", "Melakh", "Shabbat"]
# LaTeX symbols for printing the moon phase. If the phase isn't one of the quarters, then no symbol is printed.
MOON_PHASES = [r"\CIRCLE", r"\LEFTcircle", r"\Circle", r"\RIGHTcircle", r""]
# Index of the current month.
current_month_index = -1
# The current day of the month.
current_day_of_month = -1
# The current day of the week.
current_day_of_week = 0

# This counter is used for naming the tidal plot images.
image_counter = 0

# Get a list of all "ocean" pictures.
ocean_images_dir = "ocean_images/"
ocean_images = []
for o in listdir(str(Path(ocean_images_dir).resolve())):
    ocean_images.append(ocean_images_dir + o)

# Begin building the document with the LaTeX preamble.
tex = r"\documentclass[11pt,letterpaper,landscape,openany]{scrbook}\usepackage{colortbl}" \
      r"\pagenumbering{gobble}\renewcommand{\familydefault}{\sfdefault}\usepackage{tabularx}" \
      r"\usepackage[letterpaper,bindingoffset=0.2in,left=1in,right=1.25in,top=.5in,bottom=.5in,footskip=.25in," \
      r"marginparwidth=5em]{geometry}\usepackage{marginnote}\usepackage{graphicx}\usepackage{wasysym}" \
      r"\usepackage{sectsty}\usepackage{xcolor}\definecolor{hcolor}{HTML}{0A435F}" \
      r"\newcommand{\darkblue}[1]{\textcolor{hcolor}{#1}}\setkomafont{disposition}{\bfseries}" \
      r"\allsectionsfont{\centering}\newcolumntype{Y}{>{\centering\arraybackslash}X}" \
      r"\usepackage[pages=some]{background}" \
      r"\backgroundsetup{scale=1,color=black,opacity=0.4,angle=0," \
      r"contents={\includegraphics[width=\paperwidth,height=\paperheight]{title_page.jpg}}}" \
      r"\begin{document}" \
      r"\BgThispage\begin{figure}\begin{center}\Huge\darkblue{\textbf{The Aquatic Jewish Calendar}}\end{center}" \
      r"\begin{center}\Huge\darkblue{" + str(year_he) + r"}\end{center}\end{figure}\clearpage"

# Append the introduction text.
with open("intro.txt", "rt") as f:
    tex += f.read()
# This is the LaTeX data used to start a month on the page.
MONTH_TEMPLATE = r"\chapter*{\darkblue{$MONTH}}\noindent\begin{tabularx}{\textwidth}{YYYYYYY}"
# This is the LaTeX data used to insert a day into the calendar page. We'll replace each $VALUE with something useful.
CELL_TEMPLATE = r"{\normalsize\textbf{$DAY_OF_MONTH} $MOON_PHASE}\newline {\tiny{$GREGORIAN_TIME}}" \
                r"\newline\scriptsize{\textbf{$YOM_TOV}}\newline $TIDE_IMAGE"

# Create a directory for the plots if there isn't one already.
plot_directory = Path("plots")
if not plot_directory.exists():
    plot_directory.mkdir()

# Parse the spreadsheet of yom tov data.
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
    """
    Return the lunar phase of the time.
    I got this code from online and I'm not sure how it works.
    :param time_index: An index in the list of times.
    """

    lt = t[time_index]
    mi.update((lt.year, lt.month, lt.day, lt.hour, 0, 0))
    return mi.phase_name()


def get_new_month():
    """
    Returns the header for the next month.
    """

    # Reset the current day of month.
    global current_day_of_month
    current_day_of_month = 0
    # Advance to the next month.
    global current_month_index
    current_month_index += 1
    # Begin building the LaTeX data.
    month = r"\newpage\begin{figure}\includegraphics[width=\textwidth,keepaspectratio=true]{" + \
            ocean_images[current_month_index] + r"}\end{figure}\newpage" + MONTH_TEMPLATE
    # Replace $MONTH with the name of the month.
    month = month.replace("$MONTH", MONTHS[current_month_index])
    # Create the header bar with the names of the days of the week.
    for day_of_week, i in zip(DAYS_OF_WEEK, range(len(DAYS_OF_WEEK))):
        month += r"\small\cellcolor{hcolor}{\color{white}" + day_of_week + "}"
        if i < len(DAYS_OF_WEEK) - 1:
            month += "&"
        else:
            month += r"\\"
    # Conclude the header bar and begin the calendar grid.
    month += r"\end{tabularx}\\\noindent\begin{tabularx}{\textwidth}{|X|X|X|X|X|X|X|}\hline"
    # Append empty cells for all days on the grid before the first day of the month.
    # (So, if the first day of the month is Gal, add 1 blank cell, at Dag.
    for i in range(current_day_of_week):
        month += "&"
    return month


def get_start_time():
    """
    Returns the starting time of the calendar.
    """

    # Get the start of the new moon.
    q = 0
    while q < len(heights):
        if get_lunar_phase(q) == "NEW_MOON":
            break
        q += 1

    # Get the first high tide in the tidal height data.
    for j in range(q, len(heights) - 1):
        if heights[j] > heights[j - 1] and heights[j] > heights[j + 1]:
            return j
    # Oops something very bad happened.
    return -1


def get_t1(start_time):
    """
    Given the index of the start time a day, return the end of the day.
    The end of the day is two high tides hence (semidiurnal).
    :param start_time: The index of the start time.
    """

    got_middle_high_tide = False
    for j in range(start_time + 1, len(heights) - 1):
        if heights[j] >= heights[j - 1] and heights[j] > heights[j + 1]:
            # Return the second high tide.
            if got_middle_high_tide:
                return j
            # Skip the first high tide.
            else:
                got_middle_high_tide = True
    # This should never happen! If it does, then the dataset is too small.
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
    plt.savefig(plot_directory.joinpath(str(image_counter - 1) + ".png"))
    plt.clf()


def get_end_month():
    """
    Append to "tex" data to close off the monthly page.
    """
    end_of_table = ""
    # Do not start an extra row on the last month.
    if current_month_index == 11:
        end_of_table += r"\\\hline\end{tabularx}"
        return end_of_table
    if current_day_of_week > 0:
        # Fill out the last row.
        for i in range(6 - current_day_of_week):
            end_of_table += r"&"
    end_of_table += r"\\\hline\end{tabularx}"
    return end_of_table


# A list of tidal heights, mapped to "t"
heights = []
# A list of datetimes, mapped to "heights"
t = []
# Parse the tidal file.
for i, line in enumerate(tidal_data.split("\n")):
    if line == "":
        continue
    line = line.strip().split(' ')[1:]
    line = [q for q in line if q != ""]
    if len(line) == 0:
        continue
    date_string = line[0] + " " + line[1]
    # Parse the data into a datetime object and append it to t.
    t.append(parse(date_string + " GMT"))
    # Append the height data to heights.
    heights.append(float(line[2]))

# Use the max and min heights to plot consistently sized charts.
min_max_heights = np.array([min(heights), max(heights)])
min_max_range = np.arange(2)

# Turn the data into numpy arrays.
heights = np.array(heights)
t = np.array(t)

# Get the first day.
t0 = get_start_time()
# Use this to set the correct time zone.

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
    end_of_month = False
    if first_month or (moon_phase_t0 == "WANING_CRESCENT" and moon_phase_t1 == "WAXING_CRESCENT") or\
            moon_phase_t1 == "NEW_MOON":
        end_of_month = True
        moon_phase_index = 0
        # If this was the final month, stop!
        if current_month_index + 1 >= len(MONTHS):
            done = True
            tex += get_end_month()
        else:
            # Append end-of-month LaTeX data.
            if first_month:
                first_month = False
            else:
                tex += get_end_month() + r"\\"
            # Remove a blank row, if any.
            tex = tex.replace(r"\\\hline \\\hline", r"\\\hline")
            tex += get_new_month()
        if not done:
            print(f"{MONTHS[current_month_index]}: {t[t1]}")
    # Get half and quarter moon phases.
    elif moon_phase_t0 == "WAXING_CRESCENT" and moon_phase_t1 == "WAXING_GIBBOUS":
        moon_phase_index = 1
    elif moon_phase_t0 == "WAXING_GIBBOUS" and moon_phase_t1 == "WANING_GIBBOUS":
        moon_phase_index = 2
    elif moon_phase_t0 == "WANING_GIBBOUS" and moon_phase_t1 == "WANING_CRESCENT":
        moon_phase_index = 3
    # Do not show a lunar symbol.
    else:
        moon_phase_index = 4
    # If we're done, skip everything after this line.
    if done:
        continue

    # Create a "cell" in the calendar.
    calendar_cell = CELL_TEMPLATE

    calendar_day_of_month = str(current_day_of_month + 1)
    # Add a bit of vertical padding on the top.
    if current_day_of_week == 0:
        calendar_day_of_month += r"\rule{0pt}{2ex}"

    # Add the day of month.
    calendar_cell = calendar_cell.replace("$DAY_OF_MONTH", r"\darkblue{" + calendar_day_of_month + r"}")

    # Convert the printed time to the current time zone.
    d = t[t0].astimezone(tz.gettz("EST"))
    # Add the current time in the Gregorian (secular) calendar.
    calendar_cell = calendar_cell.replace("$GREGORIAN_TIME", r"\darkblue{" + d.strftime("%m.%d.%y %I:%M %p") + "}")

    # Add the moon phase, if any.
    calendar_cell = calendar_cell.replace("$MOON_PHASE", r" \hfill \darkblue{" + MOON_PHASES[moon_phase_index] + r"}")

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
            y = r"\darkblue{" + y + r"}"
            y += r"}\marginnote{\scriptsize{\darkblue{\textbf{" + y_name + r"}\newline\textit{" + y_notes + r"}}}"
        else:
            y = r"\darkblue{" + y + r"}"
        calendar_cell = calendar_cell.replace("$YOM_TOV", y)
    else:
        calendar_cell = calendar_cell.replace("$YOM_TOV", r"\vphantom{Yom Tov}")

    # Add the image.
    calendar_cell = calendar_cell.replace("$TIDE_IMAGE",
                                          r"\includegraphics[width=\linewidth,keepaspectratio=true]{plots/" +
                                          str(image_counter) + r".png}")
    # Update the tidal plot image counter.
    image_counter += 1

    # Create a new tidal plot of the heights between the times t0 and t1.
    plot(np.array(heights[t0:t1]))

    # Append the day to the LaTeX data.
    tex += calendar_cell

    current_day_of_week += 1
    # If this was the last day of the week, create a new row.
    if current_day_of_week >= len(DAYS_OF_WEEK):
        tex += r"\\\hline "
        current_day_of_week = 0
    else:
        tex += r"&"
    t0 = t1
tex += r"\end{document}"

# Write the LaTeX data to a file. You must compile it externally.
with open("calendar.tex", "wt") as f:
    f.write(tex)

print("Generated calendar.tex")

# Get all of the packages used in the .tex file.
latex_packages = re.findall(r"\\usepackage{(.*?)}", tex)
any_missing = False
# Install missing LaTeX packages.
for p in latex_packages:
    if system() == "Windows":
        try:
            installed_latex = check_output(["findtexmf", p + ".sty"])
            if installed_latex == b'':
                call(["mpm", f"--install={p}"])
                any_missing = True
        except CalledProcessError:
            call(["mpm", f"--install={p}"])
            any_missing = True
    else:
        installed_latex = check_output(["kpsewhich", p + ".sty"])
        if installed_latex == b'':
            call(["tlmgr", "install", p])
            any_missing = True
if any_missing:
    print("Installed missing LaTeX packages")

# Generate the pdf.
print("Generating pdf (this may take a while)...")
if system() == "Windows":
    call(["xelatex", "-jobname", "calendar", "calendar.tex"], stdout=open(devnull, "wb"))
else:
    call(["xelatex", "-job-name=calendar", "calendar.tex"], stdout=open(devnull, "wb"))
print("Done!")
