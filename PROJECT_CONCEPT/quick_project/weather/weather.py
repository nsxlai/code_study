"""
source: https://medium.com/robotacademy/5-tasks-to-automate-with-python-e7146996f3

Capitalization is enforced. if the city name is more than 1 word, replace the space with '+'.
This program takes the desire City name from the command line. For example:
python weather.py 'San Francisco'

From the browser,
https://wttr.in/San+Francisco

or curl from CLI
curl https://wttr.in/San+Francisco

Some terminal editor cannot support color text output. in this case the color will be displayed as ANSI code
Overcast    ←[38;5;240;1m     .--.    ←[0m ←[38;5;154m62←[0m °F←[0m        ←[38;5;240;1m  .-(    ).  ←[0m ←[1m↓←[0m
"""
import sys
import requests


if __name__ == '__main__':
    resp = requests.get(f'https://wttr.in/{sys.argv[1].replace(" ", "+")}')
    print(resp.text)
