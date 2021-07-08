"""
source: https://medium.com/analytics-vidhya/hiding-secret-keys-and-passwords-in-python-2950c6a4359
Originally, use the Medium article above for use the .env file to store secret values like username and
password information and add the .env file extension to .gitignore to prevent the information from being
uploaded to Github. This article suggested to use python-decouple library; however, this library does not
work for me (in neither Windows nor Linux). Browsing through the article response and the commenter mostly
replied with this "bloat" ware Python library is not needed. Instead using configparser, json or OS environment
variable technique will achieve the same goal.

After removing python-decouple library, I researched configparser library. This library will use the .ini
file format for standard configuration and can be added to .gitignore as well to prevent the private
development becomes public on Github. I use the following site for source:

https://docs.python.org/3/library/configparser.html

"""
from configparser import ConfigParser
FILENAME = 'secret_var_example.ini'


if __name__ == '__main__':
    config = ConfigParser()
    print(f'{config.sections() = }')
    config.read(FILENAME)
    print(f'{config.sections() = }')

    print(f'{config["DEFAULT"] = }')  # this will only return the list object
    print(f'{list(config["DEFAULT"]) = }')  # this will display all the data under 'DEFAULT'
    print(f'{config["DEFAULT"]["Compression"] = }')
    print(f'{config["userData"] = }')
    print(f'{list(config["userData"]) = }')  # List the values in userData; this also includes the DEFAULT data
    print(f'{list(config["traffic_config"]) = }')
