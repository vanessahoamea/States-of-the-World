import requests
from bs4 import BeautifulSoup
import re
import json

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
    has_density = False

    name = soup.select("span[class='mw-page-title-main']")
    country_data["name"] = name[0].get_text()

    info = soup.select("th[class='infobox-label']")
    for column in info:
        if "Capital" in column.get_text():
            value = column.next_sibling.contents[0].get_text()
            match = re.findall("([\w+\.,'\-\s]+)+", value)
            capital = match[0].replace("'", r"\'")

            country_data["capital"] = capital

        if re.match("(Official|National|Major|Vernacular).*language", column.get_text()):
            value = column.next_sibling
            try:
                value_list = value.contents[0].select("ul")[0]
                items = value_list.find_all("li")
                languages = [re.sub("[^a-zA-Z ]+", "", item.contents[0].get_text()) for item in items]
            except:
                language = value.contents[0].get_text()
                try:
                    language = language.split(":")[1].language.split("\n")[0].strip()
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
                try:
                    match = re.findall("[A-Z]{3}", value)
                    currency = match[0]
                except:
                    match = re.findall("[a-zA-Z]+\s*[a-zA-Z]+", value)
                    currency = match[0]

            country_data["currency"] = currency
        
        if "Government" in column.get_text():
            value = column.next_sibling
            government = re.sub("(\[\d+\])+", "", value.get_text())	

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

if __name__ == "__main__":
    response = requests.get(
        url="https://en.wikipedia.org/wiki/List_of_sovereign_states"
    )
    soup = BeautifulSoup(response.content, "html.parser")

    spans = soup.find_all("span", {"class": "flagicon"})
    for span in spans:
        url = span.next_sibling
        response = requests.get(
            url="https://en.wikipedia.org" + url["href"]
        )

        try:
            country_data = scrape_data(response.content)
            requests.post(
                url="http://localhost:5000/add",
                json=country_data
            )
        except Exception as e:
            print(url["href"] + " - " + str(e))