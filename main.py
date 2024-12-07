import json
import requests
from geopy import distance
import folium
import os
from dotenv import load_dotenv

def load(file_name):
    with open(file_name, "r") as my_file:
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


def coffee_place(coffee_distance):
    return coffee_distance['distance']


def distance_calculation(coords_1,file_name):
    locations = []
    n = 0
    while n < len(load(file_name)):
        location = { 'Name':load(file_name)[n]['Name'],
                     'latitude':load(file_name)[n]['Latitude_WGS84'],#широта
                     'longitude':load(file_name)[n]['Longitude_WGS84'],#долгота
                     'distance': distance.distance(coords_1, (load(file_name)[n]['Longitude_WGS84'],load(file_name)[n]['Latitude_WGS84'])).km}
        locations.append(location)
        n+=1
    return locations


def create_map(your_location, markers):
    map = folium.Map(your_location, zoom_start=14)
    for mark in markers:
        folium.Marker(
            location=(mark['latitude'],mark['longitude']),
            tooltip=mark['Name'],
            popup=mark['Name'],
            icon=folium.Icon(icon="cutlery"),
        ).add_to(map)
    map.save("index.html")


def main():
    load_dotenv()
    apikey = os.getenv('APIKEY')
    file_name = 'coffee.json'
    location_1 = input('Где вы находитесь: ')
    coords_1 = fetch_coordinates(apikey, location_1)
    sorted_coffee_list=sorted(distance_calculation(coords_1,file_name), key=coffee_place)[:5]
    create_map(list(coords_1), sorted_coffee_list)


if __name__ == '__main__':
    main()