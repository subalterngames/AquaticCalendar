# The Aquatic Jewish Calendar

![Tishrei](Tishrei.png)

**[Download the calendar here.](https://github.com/subalterngames/AquaticCalendar/releases/download/5781/calendar.pdf)**

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

- Python 3.7+
- XeLaTeX

### How to run the program

```python
python3 aquatic_calendar_creator.py -s [TIDAL STATION ID]
```

This will generate a `calendar.pdf` file.

### Optional arguments

| Argument | Description | Default |
| --- | --- | --- |
| `-s` | [Tidal station ID](https://tidesandcurrents.noaa.gov/stations.html?type=Water+Levels) | `8443970` (Boston) |


# Changelog

#### 5782

- Updated the calendar for the year 5782.
- Fixed a minor bug with setting the starting lunar state.

#### 5781

- Updated the calendar for the year 5781.
- **Tidal data is automatically downloaded at runtime.**
  - Removed `raw_parser.py`, all files in `tide_data/`, and the `-t` argument  (you no longer need to download tidal data and convert it to a csv file.)
  - Added argument `-s` (tidal stationID). 
- The (terrestrial) Jewish year is automatically determined via an online API.
  - Removed the `-y` argument (no longer needed).
- Missing Python modules are now automatically installed at runtime.
- Missing LaTeX packages are now automatically installed at runtime.
- calendar.pdf is now automatically created (rather than having to run pdflatex externally).
- Removed argument `-p` (now, tidal plots are always automatically generated).
- Fixed: Lunar phase is inaccurate (now using `pylunar` module)
- Fixed: Rare bug in which there could be too many high tides in a day.

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