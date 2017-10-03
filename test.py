#!virtualenv/bin/python3

import json
import os
import time
import unittest

import alexa_metrolink_skill

class MetrolinkTest(unittest.TestCase):

    @unittest.skip('slow test')
    def test_all_stops_are_resolvable(self):
        with open(os.path.join(os.path.dirname(__file__), 'stop-names.json')) as stop_names_file:
            stop_names = json.load(stop_names_file).keys()
        for stop_slug in stop_names:
            time.sleep(1) # avoid rate limit
            alexa_metrolink_skill.get_tram_stop_info(stop_slug)

    def test_match(self):
        self.assertEqual(
            ('Deansgate - Castlefield', 'deansgate-castlefield'),
            alexa_metrolink_skill.match_tram_stop('Deansgate')
        )

    def test_simple(self):
        print(alexa_metrolink_skill.handle_request({
            "session": {
                "new": False,
                "sessionId": "SessionId.f5aa9e6b-19a5-477d-934c-f2eb54b60885",
                "application": {
                    "applicationId": "amzn1.ask.skill.dummy"
                },
                "attributes": {},
                "user": {
                    "userId": "amzn1.ask.account.dummy"
                }
            },
            "request": {
                "type": "IntentRequest",
                "requestId": "EdwRequestId.dummy",
                "intent": {
                    "name": "TramTime",
                    "slots": {
                        "TramStop": {
                            "name": "TramStop",
                            "value": "new Islington"
                        }
                    }
                },
                "locale": "en-GB",
                "timestamp": "2017-10-02T23:14:48Z"
            },
            "context": {
                "AudioPlayer": {
                    "playerActivity": "IDLE"
                },
                "System": {
                    "application": {
                        "applicationId": "amzn1.ask.skill.dummy"
                    },
                    "user": {
                        "userId": "amzn1.ask.account.dummy"
                    },
                    "device": {
                        "supportedInterfaces": {}
                    }
                }
            },
            "version": "1.0"
        }, {}))


if __name__ == '__main__':
    unittest.main()
