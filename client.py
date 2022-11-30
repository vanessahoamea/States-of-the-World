import requests
import json
import urllib.parse

if __name__ == "__main__":
    text = "Enter an endpoint followed by the necessary parameters, separated by commas\n"
    text += "Example: top-10 density -> returns the top 10 most densely populated countries\n"
    text += "         all language=English,time_zone=UTC -> returns all countries where English is spoken and the time zone is UTC\n"
    print(text)
    
    while True:
        command = input().lower().strip()

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

        response = requests.get(
            url="http://localhost:5000/" + endpoint
        )
        response_json = json.loads(response.text)
        response_json = json.dumps(response_json, indent=2)
        print(response_json)