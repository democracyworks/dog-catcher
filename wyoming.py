import urllib
import re
import sys
import dogcatcher
import HTMLParser
import os

h = HTMLParser.HTMLParser()

cdir = os.path.dirname(os.path.abspath(__file__)) + "/"

#The following section grabs the website and writes it to a file. (Writing it to a file isn't strictly necessary, but saves some time down the line.)

file_path = cdir + "wyoming-clerks.html"
url = "http://soswy.state.wy.us/Elections/CountyClerks.aspx"

voter_state = "WY"
source = "State"

data = urllib.urlopen(url).read()
output = open(file_path,"w")
output.write(data)
output.close()

result = [("authority_name", "first_name", "last_name", "county_name", "fips",
    "street", "city", "address_state", "zip_code",
    "po_street", "po_city", "po_state", "po_zip_code",
    "reg_authority_name", "reg_first", "reg_last",
    "reg_street", "reg_city", "reg_state", "reg_zip_code",
    "reg_po_street", "reg_po_city", "reg_po_state", "reg_po_zip_code",
    "reg_phone", "reg_fax", "reg_email", "reg_website", "reg_hours",
    "phone", "fax", "email", "website", "hours", "voter_state", "source", "review")]

data = open(file_path).read()

county_data_re = re.compile("(<div>[a-zA-z\s\.]+<br />.+?)</div>", re.DOTALL)

po_re = re.compile("[\s]*(.*?P\.O\..+?)<br />")
city_re = re.compile("[\s]*(.*?),.+?\d{5}[-\d]*?[\s]*<")
state_re = re.compile("[\s]*.*?, (.+?) \d{5}[-\d]*?[\s]*<")
zip_re = re.compile("[\s]*.+?(\d{5}[-\d]*?)[\s]*<")
street_re = re.compile("</b><br />[\s]*(.+?)<br />", re.DOTALL)

address_re = re.compile("[^\n]+\d.+? [A-Z]{2,2} \d{5}[\d-]*?<", re.DOTALL)
csz_re = re.compile(".+? [A-Z]{2,2} \d{5}[\d-]*?<")

email_re = re.compile("a href=\"mailto:(.+?)\"")

website_re = re.compile("a href=\"(.+?)\">Website")
slash_re = re.compile("[^/]/[^/]")

official_name_re = re.compile("<div>(.+?)<br />",re.DOTALL)
middle_name_re = re.compile(" ([a-zA-z]\. )")

fax_re = re.compile("Fax (\d{3}\.\d{3}\.\d{4})")
phone_re = re.compile("Ph. (.+?)<br />", re.DOTALL)
extension_re = re.compile("\d([^\d][^\d]+?)\d")

county_re = re.compile("<b>(.+?) County Clerk")


county_data = county_data_re.findall(data)

for county in county_data:

	authority_name, first_name, last_name, county_name, town_name, fips, street, city, address_state, zip_code, po_street, po_city, po_state, po_zip_code, reg_authority_name, reg_first, reg_last, reg_street, reg_city, reg_state, reg_zip_code, reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code, reg_phone, reg_fax, reg_email, reg_website, reg_hours, phone, fax, email, website, hours, review = dogcatcher.begin(voter_state)

	county_name = county_re.findall(county)[0]

	authority_name = "County Clerk"

	official_name = official_name_re.findall(county)[0]
	first_name, last_name, review = dogcatcher.split_name(official_name, review)

	email = dogcatcher.find_emails(email_re, county)
	website = dogcatcher.find_website(website_re, county)
	phone = dogcatcher.find_phone(phone_re, county)
	fax = dogcatcher.find_phone(fax_re, county)

	#This section finds the full address. After finding the address, it identifies a city/state/zip (csz) combination and a PO Box number if that exists.
    #It removes both the CSZ and the PO Address (if it exists) from the full address, leaving behind a street address with some garbage.
    #It then cleans up the street address and pulls the city, state, and zip out of the csz, and assigns them as appropriate to the street address and state.

	address = address_re.findall(county)[0]

	csz = csz_re.findall(address)[0]

	try:
		po_street = po_re.findall(address)[0].replace("</b><p>","")
	except:
		po_street = ""

	street = address.replace(po_street,"").replace(csz,"")
	street = street.replace("<br />",", ").replace("\n",", ").replace(" ,",",").strip(" \n/,\r")

	if po_street:
		po_city = city_re.findall(csz)[0]
		po_state = state_re.findall(csz)[0]
		po_zip_code = zip_re.findall(csz)[0]
	if street:
		city = city_re.findall(csz)[0]
		address_state = state_re.findall(csz)[0]
		zip_code = zip_re.findall(csz)[0]


	fips = dogcatcher.find_fips(county_name, voter_state)

	result.append([authority_name, first_name, last_name, county_name, fips,
		street, city, address_state, zip_code,
		po_street, po_city, po_state, po_zip_code,
		reg_authority_name, reg_first, reg_last,
		reg_street, reg_city, reg_state, reg_zip_code,
		reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code,
		reg_phone, reg_fax, reg_email, reg_website, reg_hours,
		phone, fax, email, website, hours, voter_state, source, review])

#This outputs the results to a separate text file.

output = open(cdir + "wyoming.txt", "w")
for r in result:
	r = h.unescape(r)
	output.write("\t".join(r))
	output.write("\n")
output.close()