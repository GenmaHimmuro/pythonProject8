import json
import requests
from geopy import distance
import folium
import os
from dotenv import load_dotenv


def load(file_name):
    with open(file_name, "r", encoding='CP1251') as my_file:
        coffee_json = my_file.read()
    coffee = json.loads(coffee_json)
    return coffee


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def distance_calculation(user_location,file_name):
    active_file = load(file_name)
    locations = []
    n = 0
    while n < len(active_file):
        location = {
            'Name':active_file[n]['Name'],
            'latitude':active_file[n]['geoData']['coordinates'][1],
            'longitude':active_file[n]['geoData']['coordinates'][0],
            'distance': distance.distance(user_location, (active_file[n]['geoData']['coordinates'][1],
                                                     active_file[n]['geoData']['coordinates'][0])).km
        }
        locations.append(location)
        n+=1
    return locations


def coffee_place(coffee_distance):
    return coffee_distance['distance']


def sorted_coffee_list(user_location,file_name):
    top = sorted(distance_calculation((user_location[1],user_location[0]),file_name), key=coffee_place)
    nearby_top_5 = []
    n=0
    while n<5:
        nearby_top_5.append(top[n])
        n+=1
    return nearby_top_5


def create_map(user_location, markers):
    m = folium.Map((user_location[1],user_location[0]), zoom_start=10)
    for mark in markers:
        folium.Marker(
            location=(mark['latitude'],mark['longitude']),
            tooltip=mark['Name'],
            popup=mark['Name'],
            icon=folium.Icon(icon="cutlery"),
        ).add_to(m)
    m.save("index.html")


def main():
    load_dotenv()
    apikey = os.getenv('APIKEY')
    file_name = 'coffee.json'
    location_user = input('Где вы находитесь: ')
    user_location = fetch_coordinates(apikey, location_user)
    create_map(user_location, sorted_coffee_list(user_location,file_name))


if __name__ == '__main__':
    main()