import os
import urllib
import re
import sys
import HTMLParser
import json
import time
import dogcatcher

h = HTMLParser.HTMLParser()

cdir = os.path.dirname(os.path.abspath(__file__)) + "/"
tmpdir = cdir + "tmp/"

voter_state = "RI"
source = "State"

#The following section grabs the website and writes it to a file. (Writing it to a file isn't strictly necessary, but saves some time down the line.)

file_path = tmpdir + "rhode_island-clerks.html"
url = "http://www.elections.state.ri.us/canvassers/index.php"
data = urllib.urlopen(url).read()
output = open(file_path,"w")
output.write(data)
output.close()

result = [("authority_name", "first_name", "last_name", "town_name", "county_name", "fips",
    "street", "city", "address_state", "zip_code",
    "po_street", "po_city", "po_state", "po_zip_code",
    "reg_authority_name", "reg_first", "reg_last",
    "reg_street", "reg_city", "reg_state", "reg_zip_code",
    "reg_po_street", "reg_po_city", "reg_po_state", "reg_po_zip_code",
    "reg_phone", "reg_fax", "reg_email", "reg_website", "reg_hours",
    "phone", "fax", "email", "website", "hours", "voter_state", "source", "review")]

data = open(file_path).read()

data = data.replace("&nbsp;"," ").replace(",<br />",",")

#There are several minor errors caused by irregularly formatted data--this handles them.

data = data.replace("Giovanelli<br />","Giovanelli,").replace("Arusso","Arusso,").replace("Diane Addy","Diane Addy,")

town_data_re = re.compile("<tr>\s*<td.*?>.+?</tr>", re.DOTALL)
town_name_re = re.compile("<strong>(.+?)<")

official_name_re = re.compile("r />([^<>]+?),.+?<[/b]", re.DOTALL)
middle_name_re = re.compile(" ([a-zA-z]\.* )")
hours_re = re.compile(">(\d+:.+?)</td>", re.DOTALL)
email_re = re.compile("mailto:(.+?)\"")

phone_re = re.compile("Phone: (\(*\d.+?)\s*<", re.DOTALL)
fax_re = re.compile("Fax: (.+?)\s*<", re.DOTALL)

address_re = re.compile("<td.*?>.+?<td.+?<br />\s*(.+?\d{5}[\d-]*) *<br />", re.DOTALL)
csz_re = re.compile("\s*(.+?, [A-Z][A-Z] \d{5}[\d-]*)")
city_re = re.compile("(.+?),")
state_re = re.compile(" [A-Z][A-Z] ")
zip_re = re.compile("\d{5}[\d-]*")
po_re = re.compile("P\.*O\.* .+")

name_line_re = re.compile("\d\s*<br />\s+([^\d]+)</td")

authority_name_re = re.compile(",\s+([^\d]+?)</td>")
space_re = re.compile("\s\s+")

#This splits the complete dataset into a series of towns so we can extract data form them one-by-one.

town_data = town_data_re.findall(data)

for town in town_data:
	authority_name, first_name, last_name, county_name, town_name, fips, street, city, address_state, zip_code, po_street, po_city, po_state, po_zip_code, reg_authority_name, reg_first, reg_last, reg_street, reg_city, reg_state, reg_zip_code, reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code, reg_phone, reg_fax, reg_email, reg_website, reg_hours, phone, fax, email, website, hours, review = dogcatcher.begin(voter_state)

	name_line = name_line_re.findall(town)[0].replace("<br />","")
	first_name, last_name, authority_name, review = dogcatcher.make_name(name_line, ",", review)

	#Some of the authority names break in mid-line; this cleans them.

	for item in space_re.findall(authority_name):
		authority_name = authority_name.replace(item," ")

	town_name = town_name_re.findall(town)[0]


	hours = hours_re.findall(town)[0]
	hours = " ".join(hours.replace("\r\n","").replace("<br />"," ").split())

	email = dogcatcher.find_emails(email_re, town)

	phone = dogcatcher.find_phone(phone_re, town)
	fax = dogcatcher.find_phone(fax_re, town)

    #This section finds athe address. After finding the address, it identifies a city/state/zip (csz) combination and a PO Box number if that exists.
    #It removes both the CSZ and the PO Address (if it exists) from the full address, leaving behind a street address with some garbage.
    #It then cleans up the street address and pulls the city, state, and zip out of the csz, and assigns them as appropriate to the street address and state.

	address = address_re.findall(town)[0]

	csz = csz_re.findall(address)[0]

	if po_re.findall(address):
		po_street = " ".join(po_re.findall(address)[0].replace("<br />","").strip(", ").split())
	else:
		po_street = ""

	street = address.replace(po_street,"").replace(csz,"").replace("</b>","")
	street = " ".join(street.replace("<br />",", ").split()).strip(", ")

	if po_street:
		if street:
			city = city_re.findall(csz)[0].strip()
			address_state = state_re.findall(csz)[0].strip()
			zip_code = zip_re.findall(csz)[0].strip()
		po_city = city_re.findall(csz)[0].strip()
		po_state = state_re.findall(csz)[0].strip()
		po_zip_code = zip_re.findall(csz)[0].strip()
	else:
		city = city_re.findall(csz)[0].strip()
		address_state = state_re.findall(csz)[0].strip()
		zip_code = zip_re.findall(csz)[0].strip()


	fips, county_name = dogcatcher.map_fips(town_name, voter_state, zip_code)

	result.append([authority_name, first_name, last_name, town_name, county_name, fips,
	street, city, address_state, zip_code,
	po_street, po_city, po_state, po_zip_code,
	reg_authority_name, reg_first, reg_last,
	reg_street, reg_city, reg_state, reg_zip_code,
	reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code,
	reg_phone, reg_fax, reg_email, reg_website, reg_hours,
	phone, fax, email, website, hours, voter_state, source, review])

#This outputs the results to a separate text file.
dogcatcher.output(result, voter_state, cdir)
