# source: https://medium.com/@krisshaffer/a-journey-through-api-programming-part-3-retrieving-data-84b23736b0df
import requests
import json


if __name__ == '__main__':
    raw_data = requests.get('https://hypothes.is/api/search?limit=200&user=gluejar@hypothes.is')
    parsed_data = json.loads(raw_data.text)
    print(parsed_data)