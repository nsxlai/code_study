import requests

URL = 'http://ip.jsontest.com/'

'''Dark Sky API'''
api_key = '7b684b392b7e45f3878280a8dbb2d978'
# Location
home_city = 'Fremont'
location = {home_city: {'latitude': 37.5483, 'longitude': -121.9886, 'tz': -7},
            'Milpitas'     : {'latitude': 37.4323, 'longitude': -121.8995, 'tz': -7},
            'New York': {'latitude': 42.3601, 'longitude': -71.0589, 'tz': -4},
            'Los Angeles': {'latitude': 34.0522, 'longitude': -118.243685, 'tz': -7},
            'San Francisco': {'latitude': 37.7740, 'longitude': -122.4313, 'tz': -7},
            'Hong Kong': {'latitude': 22.3964, 'longitude': 114.109497, 'tz': 8},
            'Paris': {'latitude': 48.8566, 'longitude': 2.3522, 'tz': 2},
            'Taipei': {'latitude': 25.1055, 'longitude': 121.5974, 'tz': 8},
            'Tokyo': {'latitude': 35.6528, 'longitude': 139.8395, 'tz': 9}
            }

weather_icon = {'partly-cloudy-night': '4', 'partly-cloudy-day': 'H', 'cloudy': 'N',
                'rain': 'R', 'snow': 'X', 'clear-night': '2', 'clear-day': 'B',
                'windy': 'F', 'fog': 'L', 'celsius': '*', 'fehrenheit': '+', 'thermo': "'",
                'sunrise': 'J', 'sunset': 'A', }


def get_weather_report(city, latitude, longitude):
    """Fetch the weather information from Darksky.net"""
    api_url = 'https://api.darksky.net/forecast/{}/{},{}'.format(api_key, latitude, longitude)
    req_data = requests.get(api_url)
    req_data = req_data.json()

    # Debug message
    print('Summary: {}'.format(req_data['currently']['summary']))
    print('Icon: {}'.format(req_data['currently']['icon']))
    print('Location: {}'.format(city))
    print('Latitude: {}'.format(req_data['latitude']))
    print('Longitude: {}'.format(req_data['longitude']))
    print('Temperature: {}'.format(req_data['currently']['temperature']))
    print('Humidity: {}'.format(req_data['currently']['humidity']))
    print('Pressure: {}'.format(req_data['currently']['pressure']))
    print('Rain Chance: {}'.format(req_data['currently']['precipProbability']))
    print('Wind Speed: {}'.format(req_data['currently']['windSpeed']))
    print('Wind Bearing: {}'.format(req_data['currently']['windBearing']))
    return req_data


if __name__ == '__main__':
    city = 'Fremont'
    req_data = get_weather_report(city, location[city]['latitude'], location[city]['longitude'])
    print(req_data)