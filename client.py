"""
This module provides an interface that allows a client to make requests 
to the States of the World API.
"""

__version__ = "0.1"
__author__ = "Vanessa Hoamea"

import json
import urllib.parse
import requests

"""
The main function that allows the user to interact with the API
by inputting commands and receiving data in JSON format.
"""
if __name__ == "__main__":
    text = "Enter an endpoint followed by the necessary parameters, " \
           "separated by commas\n"
    text += "Example: top-10 density -> returns the top 10" \
            "most densely populated countries\n"
    text += "\t all language=English,time_zone=UTC -> returns all" \
            "countries where English is spoken and the time zone is" \
            "UTC\n"
    print(text)
    
    while True:
        command = input().lower().strip()

        # The client shuts down when the user inputs "quit"
        if command == "quit":
            break

        # Validating the user's input
        if command[:6] == "top-10":
            endpoint = command.replace(" ", "/")
        else:
            if command.count(" ") != 1 or command.count("=") == 0:
                print("Incorrect format")
                continue
            
            endpoint = command.split(" ")[0]
            parameters = command.split(" ")[1]
            parameters_dict = {}
            
            try:
                parameters = parameters.split(",")
            except:
                parameters = [parameters]
            
            for pair in parameters:
                parameters_dict[pair.split("=")[0]] = pair.split("=")[1]
            
            endpoint += "?" + urllib.parse.urlencode(parameters_dict)

        # Making the API call to retrieve the data then printing it
        response = requests.get(
            url="http://localhost:5000/" + endpoint
        )
        response_json = json.loads(response.text)
        response_json = json.dumps(response_json, indent=2)
        print(response_json)