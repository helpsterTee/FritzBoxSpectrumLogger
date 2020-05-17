# FritzBoxSpectrumLogger
A logger and video generator for spectrum graphics from FritzBox routers

## Installation
- Python3
- `pip install -r requirements.txt`
- Modify run.py with the URL of your FritzBox (defaults to http://fritz.box), username and password (only method supported for now)

## Usage
- Start logging: `python run.py`
- Create timelapse video of spectrum changes: `python video.py timestamp_from timestamp_to`
