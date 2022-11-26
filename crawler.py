import requests
from bs4 import BeautifulSoup
import re

def scrape_data(content):
	soup = BeautifulSoup(content, "html.parser")
	country_data = {
		"name": None,
		"capital": None,
		"language": [],
		"population": None,
		"density": None, #per km2
		"area": None, #km2
		"time_zone": None,
		"currency": None,
		"government": None
	}

	name = soup.select("span[class='mw-page-title-main']")
	country_data["name"] = name[0].get_text()

	info = soup.select("th[class='infobox-label']")
	for column in info:
		if "Capital" in column.get_text():
			value = column.next_sibling
			value_list = value.find_all("a")
			for item in value_list:
				item = item.get_text()
				if re.match("^[A-Z][a-zA-Z-,. ]*$", item):
					capital = item
					break

			country_data["capital"] = capital

		if "language" in column.get_text().lower():
			value = column.next_sibling
			try:
				value_list = value.contents[0].select("ul")[0]
				items = value_list.find_all("li")
				languages = [re.sub("[^a-zA-Z ]+", "", item.get_text()) for item in items]
			except:
				language = value.contents[0].get_text()
				languages = [language]

			country_data["language"].extend(languages)
		
		if "Time zone" in column.get_text():
			value = column.next_sibling.get_text().replace("−", "-")
			match = re.findall("([A-Z]+(\+|-)\d+(:\d+)?).*$", value)
			time_zone = match[0][0]
			
			country_data["time_zone"] = time_zone
		
		if "Currency" in column.get_text():
			value = column.next_sibling.get_text()
			match = re.findall("\([A-Z]+\)", value)
			currency = match[0].replace("(", "").replace(")", "")

			country_data["currency"] = currency
		
		if "Government" in column.get_text():
			value = column.next_sibling
			government = value.get_text()
			try:
				government = government.split("[")[0]
			except:
				pass

			country_data["government"] = government

	info = soup.select("th[class='infobox-header']")
	for column in info:
		if "Population" in column.get_text():
			values = column.parent.next_sibling
			population = values.contents[1].get_text()
			try:
				population = population.split("[")[0]
			except:
				pass

			while "Density" not in values.contents[0].get_text():
				values = values.next_sibling
			density = values.contents[1].get_text().split("/")[0]

			country_data["population"] = int(population.replace(",", ""))
			country_data["density"] = float(density)

		if "Area" in column.get_text():
			values = column.parent.next_sibling
			area = values.contents[1].get_text()
			try:
				area = area.split("[")[0]
			except:
				pass
			area = area.split()[0]
			country_data["area"] = int(area.replace(",", ""))
		
	return country_data

if __name__ == "__main__":
	response = requests.get(
		url="https://en.wikipedia.org/wiki/Switzerland",
	)

	scrape_data(response.content)