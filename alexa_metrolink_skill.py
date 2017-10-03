#!/usr/bin/env python3

from bs4 import BeautifulSoup
import difflib
import itertools
import json
import os
import requests

with open(os.path.join(os.path.dirname(__file__), 'stop-names.json')) as stop_names_file:
    STOPS = json.load(stop_names_file)


def match_tram_stop(name):
    name = name.lower()
    all_names = list(itertools.chain(*(stop['alternatives'] for stop in STOPS.values())))
    possibilities = difflib.get_close_matches(name, all_names)
    if len(possibilities) == 0:
        return None
    matched_name = possibilities[0]
    for slug, stop in STOPS.items():
        if matched_name in stop['alternatives']:
            return (stop['name'], slug)
    else:
        return None


def get_tram_line_info():
    return requests.get('http://beta.tfgm.com/api/statuses/tram').json().get('items', [])


def format_tram_wait(wait):
    if wait == 'Departing' or wait == 'Arrived':
        return 0
    else:
        return int(wait)


def get_tram_stop_info(stop):
    departure_board = BeautifulSoup(
        requests.get('https://beta.tfgm.com/public-transport/stations/{}-tram?layout=false'.format(stop)).text,
        "html.parser"
    ).find(id='departure-items')

    if departure_board:
        return [
            {
                'destination': departure.find("td", {"class":"departure-destination"}).text,
                'carriages': departure.find("td", {"class": "departure-carriages"}).find("span").text,
                'wait': format_tram_wait(
                    departure.find("td", {"class": "departure-wait"}).find("span", {"class":"figure"}).text
                ),
            }
            for departure in departure_board.find_all('tr')
        ]
    else:
        return []


def tram_line_info_request():
    try:
        lines = get_tram_line_info()
    except:
        return "Sorry, I couldn't get the latest tram information"
    else:
        if lines:
            return " ".join("{}: {}.".format(line['name'], line['status']) for line in lines)
        else:
            return "There are no updates published at present"


def format_tram(tram):
    carriages = tram['carriages'].lower()
    destination = tram['destination']
    wait = tram['wait']
    if wait == 0:
        wait_text = 'now'
    elif wait == 1:
        wait_text = 'in 1 minute'
    else:
        wait_text = 'in {} minutes'.format(wait)

    if destination == 'See Tram Front':
        destination = 'an unknown destination'

    return '{} tram to {} leaving {}'.format(carriages, destination, wait_text)


def tram_stop_info_request(stop_name):
    match = match_tram_stop(stop_name)
    if match is None:
        return "Sorry, I didn't recognise that tram stop name."
    stop_name, slug = match

    departures = get_tram_stop_info(slug)
    if len(departures) == 0:
        return "I couldn't find any upcoming departures from {}".format(stop_name)
    elif len(departures) == 1:
        return "The next tram from {} is a {}".format(stop_name, format_tram(departures[0]))
    else:
        response = "The next trams from {} are:".format(stop_name)
        response += ', '.join('a {}'.format(format_tram(departure)) for departure in departures)
        return response


def build_response(speech_response):
    return {
        "version": "1.0",
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": speech_response
            }
        }
    }


def handle_request(event, context):
    # verify_application_id(event)

    if event["request"]["type"] == "LaunchRequest":
        return build_response(tram_line_info_request())
    elif event["request"]["type"] == "IntentRequest":
        intent_name = event['request']['intent']['name']
        if intent_name == 'TramStatus':
            return build_response(tram_line_info_request())
        elif intent_name == 'TramTime':
            return build_response(
                tram_stop_info_request(
                    event['request']['intent']['slots'].get('TramStop', {'value': 'unknown'})['value']
                )
            )
