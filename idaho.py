import urllib
import re
import sys
import dogcatcher
import HTMLParser
import os

h = HTMLParser.HTMLParser()

cdir = os.path.dirname(os.path.abspath(__file__)) + "/"



voter_state = "ID"
source = "State"

#The following section grabs the website and writes it to a file. (Writing it to a file isn't strictly necessary, but saves some time down the line.)

file_path = cdir + "idaho-counties.html"
url = "http://www.idahovotes.gov/clerk.htm"
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

county_re = re.compile("\n\s*<p>[^\n]+?<br>.+?</a> *</p>", re.DOTALL)
county_name_re = re.compile("(.+?) County Clerk")

official_name_re = re.compile("<p>(.+) *<br>")

email_re = re.compile("a href=\"mailto:(.+?)\"")
website_re = re.compile("(http://.+?)\"")

phone_re = re.compile("phone: (.+) *<br>")
fax_re = re.compile("fax: (.+) *<br>")

address_re = re.compile("Clerk<br>\s+(.+\d{5}[\d-]*) *<br>\s+phone", re.DOTALL)
csz_re = re.compile(" *([^,\n]+? [A-Z][A-Z] *\d{5}[\d-]*)")
city_re = re.compile("(.+?) [A-Z][A-Z]")
state_re = re.compile(" ([A-Z][A-Z]) ")
zip_re = re.compile(" (\d{5}[\d-]*)")
po_re = re.compile("(PO Box .+) *<br>", re.DOTALL)

#fixes an edge case in Washington County
data = data.replace("</strong>","").replace("<td valign=\"top\">","<p>").replace("Email</a><br>","Email</a></p>")

county_data = county_re.findall(data)

for county in county_data:

	authority_name, first_name, last_name, county_name, town_name, fips, street, city, address_state, zip_code, po_street, po_city, po_state, po_zip_code, reg_authority_name, reg_first, reg_last, reg_street, reg_city, reg_state, reg_zip_code, reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code, reg_phone, reg_fax, reg_email, reg_website, reg_hours, phone, fax, email, website, hours, review = dogcatcher.begin(voter_state)

	authority_name = "County Clerk"

	print "_______________________________"
	print county
	print "+++++++++++++++++++++++++++++++"
	
	county_name = county_name_re.findall(county)[0].strip()
	print county_name

	official_name = official_name_re.findall(county)[0].lstrip("\n ")
	first_name, last_name, review = dogcatcher.split_name(official_name, review)

	email = dogcatcher.find_emails(email_re, county)

	website = dogcatcher.find_website(website_re, county)

	phone = dogcatcher.find_phone(phone_re, county)

	fax = dogcatcher.find_phone(fax_re, county)

	#This section finds athe address. After finding the address, it identifies a city/state/zip (csz) combination and a PO Box number if that exists.
	#It removes both the CSZ and the PO Address (if it exists) from the full address, leaving behind a street address with some garbage.
	#It then cleans up the street address and pulls the city, state, and zip out of the csz, and assigns them as appropriate to the street address and state.

	address = address_re.findall(county)[0]

	csz = csz_re.findall(address)[0]

	try:
		po_street = po_re.findall(address)[0].replace(csz,"").strip(", \n")
	except:
		po_street = ""

	street = address.replace(po_street,"").replace(csz,"").replace("<br>",", ")
	street = street.replace("\n",", ").replace("\r","").replace(" ,",",").strip(" \n/,")

	if po_street:
		po_city = city_re.findall(csz)[0].strip()
		po_state = state_re.findall(csz)[0].strip()
		po_zip_code = zip_re.findall(csz)[0].strip()
	if street:
		city = city_re.findall(csz)[0].strip()
		address_state = state_re.findall(csz)[0].strip()
		zip_code = zip_re.findall(csz)[0].strip()


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

output = open(cdir + "idaho.txt", "w")
for r in result:
	r = h.unescape(r)
	output.write("\t".join(r))
	output.write("\n")
output.close()