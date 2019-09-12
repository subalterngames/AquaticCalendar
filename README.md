# The Aquatic Jewish Calendar

![Tishrei](Tishrei.png)

**[Download the calendar here.](https://github.com/subalterngames/AquaticCalendar/releases/download/5780/calendar.pdf)**

I recently attempted to research Aquatic Judaism for a personal project, but soon realized that almost no information about the religion exists on the Internet. In response, I've created this Aquatic Jewish calendar specifically for Terrestrial Jews, as an educational aid to better understand their Aquatic brethren.

The Terrestrial and Aquatic Judaism calendars differ in some crucial respects. The secular (Gregorian) calendar is _solar_: days, months, and years are based on the Earth's movement around the Sun. The Terrestrial Jewish calendar is _lunisolar_: Each month starts at a new moon, and each day starts at sunset. The Aquatic Jewish calendar is _lunitidal_: Each month starts at a new moon, and each day starts at high tide.

The sinusoidal waves on this calendar are graphs of predicted tidal heights in Boston, Massachusetts. For most observant Aquatic Jews, this alone is insufficiently accurate. The prudent Aquatic Jew will listen for the sound of the shofar at hide tide to determine when the day has begun or ended.

All images in this calendar are from the [Met's open access collection](https://www.metmuseum.org/art/collection)

All tidal data was gathered from the [NOAA website](https://opendap.co-ops.nos.noaa.gov/axis/webservices/predictions/index.jsp)

## Contact Me

- [Twitter](https://twitter.com/subalterngames)
- [Email](subalterngames@gmail.com)
- [My website](https://subalterngames.com)

## Creating Your Own Aquatic Calendar

**[Email me](subalterngames@gmail.com) and I'll happily create a calendar for you.** 

If you want to try making your own calendar, this repo contains most of the tools required.

### Required Software

- python3
  - pathlib
  - matplotlib
  - dateutil
  - argparse
- LaTeX
  - scrbook
  - colortbl
  - tabularx
  - marginnote
  - graphicx
  - wasysym
  - sectsty
  - xcolor 
  - background

### How to run the program

```python
python3 aquatic_calendar_creator.py
```

This will generate a `.tex` file, which you can then turn into a pdf with LaTeX.

### Optional arguments

| Argument | Description | Default |
| --- | --- | --- |
| `-t <path>` | path/to/your/tidal/data.csv | `tide_data/boston_5780.csv` |
| `-p` | Create new tidal graph images. | `False` |
| `-y` | The year. | `5780` |

### Getting tidal data

1. Go to [this website](https://opendap.co-ops.nos.noaa.gov/axis/webservices/predictions/index.jsp) and gather all tidal data from one Rosh Hashanah to the next (add a few days on either end). Download the data as a text file. The station ID for Boston is: 8443970 
2. Run `raw_parser.py`, which will output a usable .csv file (you'll need to rename the file).


# Changelog

#### 5780

- Revised the calendar for the year 5780.
  - Re-plotted tidal data.
  - Revised the "intro" section.
  - Expanded some yom tov descriptions.
  - Fixed: Some typos in the yom tov descriptions.
  - Fixed: Inconsistent orthography for ח (was a mix of "ch" and "kh"; now, it is always "kh").
- Update this README:
  - Rewrote the "Getting tidal data" section.
  - Updated image of Tishrei.
  - Added more contact information.
- Improved tidal data parsing.
  - Added `tide_data/boston_5780_raw.txt` (raw NOAA data).
  - Added `tide_data/boston_5780.csv` (processed NOAA data).
  - Renamed `tide_data/boston.csv` to `tide_data/boston_5779.csv`.
  - Added `raw_parser.py` to parse raw NOAA data.
- Improved `aquatic_calendar_creator.py`
  - Made the calculation of the first hour of the year more flexible.
  - Fixed: Sometimes too many tidal plot images are generated.
  - Fixed: If the last week of the month ends on Shabbat, an extra blank row is generated.