from bs4 import BeautifulSoup
import requests
import csv

#634

def load(url):

	return requests.get(url).text

def makeSoup(text):

	return BeautifulSoup(text, "html.parser")

def scrape_spans(url):

	soup = makeSoup(load(url))

	return soup.find_all("span")

def scrape_spans(url):

	soup = makeSoup(load(url))

	return soup.find_all("span")

def scrape_tables(url):

	soup = makeSoup(load(url))

	return soup.find_all("table")

def scrape_unit_tables(soup):

	tables = soup.find_all("table")
	# print(len(js))
	return tables[0], tables[1]

def scrape_unit_attributes(soup):

	attributes_list = soup.find_all("dl")[0]

	attributes = [dd.text.strip().replace("\n", "") for dd in attributes_list.find_all("dd")]

	return attributes

if __name__ == '__main__':

	url = "https://wiki.totalwar.com/w/Units_in_Medieval_II:_Total_War.html"

	url_prefix = url.split("/w/")[0]

	# fields = ["Country"]

	#Gets Country Names
	span_headings = [span.text for span in scrape_spans(url)]
	nations = [span_headings[i] for i in range(len(span_headings)) if i >= 40 and i <= 56]

	#finds all tables within the url
	main_tables = scrape_tables(url)

	#Keeps track of current country
	nation_index = -1

	#Stores unit information
	all_units = []

	#ERROR IN THIS LOOP

	#loop through tables
	for table in main_tables:

		#Skips tables that don't contain a unit category
		if table.find("th") == None:

			continue

		#Increase nation_index when light infantry found
		if table.find("th").text.strip() == "Light infantry":

			nation_index += 1

		#iterrate through frows of the table
		for row in table.find_all("tr"):

			#iterrate through tds of table
			for item in row.find_all("td"):

				if item.find("a") == None:

					continue

				all_units.append((nations[nation_index], url_prefix + item.find("a")["href"]))

	#Stores all unit information for saving
	all_entries = []

	#List of headings that will be updated as new ones found
	fields = ["Country", "Name"]

	#Accounts for siege, cavlary, ranged units having secondary/teriary weapons
	attack_types = ["Primary", "Secondary", "Teriary"]

	#Loop through the country and url of all units
	for country, unit_url in all_units:

		if country not in [a[0] for a in all_entries]:

			print(country)

		unit_soup = makeSoup(load(unit_url))

		current_entry = [None for i in fields]
		current_entry[0] = country

		#scrape unit info
		all_info = []

		for table in scrape_unit_tables(unit_soup):

			for table_row in table.find_all("tr"):

				table_row = str(table_row.text).replace("\n", "").strip()

				all_info.append(table_row)

		attack_indexes = [index for index in range(len(all_info)) if all_info[index].find("Attack:") != -1]

		for index, a in enumerate(attack_indexes):

			all_info[a] = all_info[a].replace("Attack:", attack_types[index] + "_" + "Attack:")

		for index, item in enumerate(all_info):

			if index == 0:

				#check early/late

				h2 = unit_soup.find_all("h2")[0].text.lower()

				if h2.find("early") != -1:

					print("boop")

					item += " Early"

				if h2.find("late") != -1:

					item += " Late"

					print("boop")

				current_entry[fields.index("Name")] = item

				continue

			if item.find(":") == -1:

				continue

			heading, information = item.split(": ")

			if heading not in fields:

				fields.append(heading)

				current_entry.append(None)

			current_entry[fields.index(heading)] = information

		for attribute in scrape_unit_attributes(unit_soup):

			if attribute not in fields:

				fields.append(attribute)

				current_entry.append(None)

			current_entry[fields.index(attribute)] = True

		all_entries.append(current_entry)

	filename = "units.csv"

	with open(filename, "w") as csvfile:

		csvwriter = csv.writer(csvfile)

		csvwriter.writerow(fields)
		csvwriter.writerows(all_entries)
	# #table 0 unit costs/class
	# #table 1 unit stats

	# l = []

	# skip = [" ", "Attack", "Defence"]

	# blank_entry = []

	# all_info = []

	# for table in scrape_unit_tables(url):

	# 	for table_row in table.find_all("tr"):

	# 		table_row = str(table_row.text).replace("\n", "").strip()

	# 		all_info.append(table_row)

	# print(all_info)

	# fields = ["Name"]

	# current_entry = [None for i in fields]

	# for index, item in enumerate(all_info):

	# 	if index == 0:

	# 		current_entry[fields.index("Name")] = item

	# 		continue

	# 	if item.find(":") == -1:

	# 		continue

	# 	heading, information = item.split(": ")

	# 	if heading not in fields:

	# 		fields.append(heading)

	# 		current_entry.append(None)

	# 	current_entry[fields.index(heading)] = information

	# print(fields)
	# print(current_entry)