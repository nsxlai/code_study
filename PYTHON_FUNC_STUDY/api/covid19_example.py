# source: https://towardsdatascience.com/json-and-apis-with-python-a3282aa75963
import requests
from pprint import pprint
import pandas as pd


if __name__ == '__main__':
    url = 'https://api.covid19api.com/summary'
    response = requests.get(url).json()
    print(response.keys())
    country_list = [detail['Country'] for detail in response['Countries']]
    # pprint(country_list)
    # pprint(response['Countries'])
    covid19_world = pd.DataFrame(response['Countries'])
    # print(covid19_world.iloc[177])  # USA
    covid19_usa = covid19_world[covid19_world['Country']=='United States of America'].T
    print(covid19_usa)

