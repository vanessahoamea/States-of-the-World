"""
This module handles the web scraping part of the project. It extracts
relevant information about various countries and stores it in the 
database.
"""

__version__ = "0.1"
__author__ = "Vanessa Hoamea"

import re
import json
import requests
from bs4 import BeautifulSoup

"""
Scrapes the Wikipedia page passed as a parameter and returns a dict
containing all the necessary information found on the page.
"""
def scrape_data(content):
    soup = BeautifulSoup(content, "html.parser")
    country_data = {
        "name": None,
        "capital": None,
        "language": None,
        "population": None,
        "density": None,
        "area": None,
        "time_zone": None,
        "currency": None,
        "government": None
    }

    # The country's name can be extracted from the page title
    name = soup.select("span[class='mw-page-title-main']")
    country_data["name"] = name[0].get_text()

    # The other attributes will be extracted from the infobox
    info = soup.select("th[class='infobox-label']")
    for column in info:
        if "Capital" in column.get_text():
            value = column.next_sibling.contents[0].get_text()
            match = re.findall("([\w+\.,'\-\s]+)+", value)
            capital = match[0].replace("'", r"\'").replace("\n", "").strip()

            country_data["capital"] = capital

        language_regex = "(Official|National|Major|Vernacular).*language"
        if re.match(language_regex, column.get_text()):
            if (country_data["language"] == None 
                    or "None" in country_data["language"]):
                # In case an infobox has multiple language sections, we will
                # only extract languages from the first one we find to avoid
                # adding too much/useless information to the database
                value = column.next_sibling
                try:
                    value_list = value.contents[0].select("ul")[0]
                    items = value_list.find_all("li")
                    for item in items:
                        item_text = item.contents[0].get_text()
                        languages.append(re.sub("[^a-zA-Z ]+", "", item_text))
                except:
                    language = value.contents[0].get_text()
                    try:
                        language = (language.split(":")[1].
                                             split("\n")[0].
                                             strip())
                    except:
                        pass
                    languages = [language]

                country_data["language"] = json.dumps(languages)
        
        if "Time zone" in column.get_text():
            value = column.next_sibling.get_text().replace("−", "-")
            match = re.findall("([A-Z]+(\+|-)\d+(:\d+)?).*$", value)
            if match == []:
                match = re.findall("([A-Z]+).*$", value)
                time_zone = match[0]
            else:
                time_zone = match[0][0]
            
            country_data["time_zone"] = time_zone
        
        if "Currency" in column.get_text():
            value = column.next_sibling.get_text()
            if country_data["currency"] == None:
                # Same as with the languages, only the first value is
                # relevant
                try:
                    match = re.findall("[A-Z]{3}", value)
                    currency = match[0]
                except:
                    match = re.findall("[a-zA-Z]+\s*[a-zA-Z]+", value)
                    currency = match[0]

            country_data["currency"] = currency
        
        if "Government" in column.get_text():
            value = column.next_sibling
            government = re.sub("(\[.+\])+", "", value.get_text())

            country_data["government"] = government

    info = soup.select("th[class='infobox-header']")
    for column in info:
        if "Population" in column.get_text():
            values = column.parent.next_sibling
            population = values.contents[1].get_text()
            population = re.findall("[0-9,]+", population)[0]
            country_data["population"] = int(population.replace(",", ""))

            try:
                while "Density" not in values.contents[0].get_text():
                    values = values.next_sibling
                density = values.contents[1].get_text().split("/")[0]
                country_data["density"] = float(density.replace(",", ""))
            except:
                pass

        if "Area" in column.get_text():
            values = column.parent.next_sibling
            area = values.contents[1].get_text()
            area = re.findall("[\d.,]+", area)[0]
            country_data["area"] = float(area.replace(",", ""))
        
    return country_data

"""The main function that acts as our crawler."""
if __name__ == "__main__":
    # Retrieving the list of countries
    response = requests.get(
        url="https://en.wikipedia.org/wiki/List_of_sovereign_states"
    )
    soup = BeautifulSoup(response.content, "html.parser")

    # Opening each country's page and collecting the data
    spans = soup.find_all("span", {"class": "flagicon"})
    for span in spans:
        url = span.next_sibling
        response = requests.get(
            url="https://en.wikipedia.org" + url["href"]
        )

        # Saving the country in the database by calling the /add
        # endpoint from our API
        try:
            country_data = scrape_data(response.content)
            requests.post(
                url="http://localhost:5000/add",
                json=country_data
            )
        except Exception as e:
            print(url["href"] + " - " + str(e))