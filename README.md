# FritzBoxSpectrumLogger
A logger and video generator for spectrum graphics from FritzBox routers

![sample output](https://i.imgur.com/lSFClov.gif)

## Installation
- Python3
- `pip install -r requirements.txt`
- Modify run.py with the URL of your FritzBox (defaults to http://fritz.box), username and password (only method supported for now)

## Usage
- Start logging: `python run.py`
- Create timelapse video of spectrum changes: `python video.py timestamp_from timestamp_to`

## Known issues
- It will create a log entry on session login. This may spam your FritzBox log, if used too often. Default value is every 5 Minutes.
- I still don't know what happens if the spectrum is empty after restart or connection loss :)
