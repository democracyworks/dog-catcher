import os
import urllib
import re
import sys
import dogcatcher

cdir = os.path.dirname(os.path.abspath(__file__)) + "/"
tmpdir = cdir + "tmp/"

#Every county is on a different webpage, so we have to grab every webpage. To do so, we grab a list of counties and then grab a series of web pages based on that list.
#This grabs a page containing a list of NY counties and writes it to a file. Writing it isn't strictly necessary, but saves some run time in the long run.

url = "http://www.nysegov.com/map-ny.cfm"
file_path = tmpdir + "new-york-counties.html"

data = urllib.urlopen(url).read()
output = open(file_path,"w")
output.write(data)
output.close()

voter_state = "NY"
source = "State"

result = [("authority_name", "first_name", "last_name", "county_name", "fips",
    "street", "city", "address_state", "zip_code",
    "po_street", "po_city", "po_state", "po_zip_code",
    "reg_authority_name", "reg_first", "reg_last",
    "reg_street", "reg_city", "reg_state", "reg_zip_code",
    "reg_po_street", "reg_po_city", "reg_po_state", "reg_po_zip_code",
    "reg_phone", "reg_fax", "reg_email", "reg_website", "reg_hours",
    "phone", "fax", "email", "website", "hours", "voter_state", "source", "review")]

data = open(file_path).read()

county_name_re = re.compile("Learn more about ([a-zA-Z]+)")

phone_re = re.compile("Phone: (.+?)<..>")
fax_re = re.compile("Fax: (.*?)&nbsp;&nbsp;</TH>")
official_name_re = re.compile("OFFICERS<BR><BR>(.+?)[<,]")
official_name_2_re = re.compile("<BR>(.+?),")

address_re = re.compile("Board of Elections<BR>(.+?\d{5}[-\d]*?)<br>")
csz_re = re.compile("<br>([^<>]+?, [A-Z]{2,2} +?\d{5}[\d-]*)")
city_re = re.compile("(.+?),")
state_re = re.compile(" [A-Z][A-Z] ")
zip_re = re.compile("\d{5}[\d-]*")
po_re = re.compile("(P\.\s*O\..+?)<br>")
comma_re = re.compile("[, ]{2,}")
#This reduces the web page grabbed earlier to a simple list of county names. For each county name, we then turn it into a URL, grab an associated county webpage, extract the data, add that data to the Results matrix, and move on to the next county name.

county_names = county_name_re.findall(data)

for item in county_names:

	authority_name, first_name, last_name, county_name, town_name, fips, street, city, address_state, zip_code, po_street, po_city, po_state, po_zip_code, reg_authority_name, reg_first, reg_last, reg_street, reg_city, reg_state, reg_zip_code, reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code, reg_phone, reg_fax, reg_email, reg_website, reg_hours, phone, fax, email, website, hours, review = dogcatcher.begin(voter_state)

	county_name = item

	authority_name = "Board of Elections"

	#We need to define a slightly different version of the county name to be used in the URL; there's only a distinction in two counties, St. Lawrence and New York.

	county_name_use = county_name

	if county_name == "St":
		county_name = "St. Lawrence"
		county_name_use = "St.Lawrence"
	if county_name == "New":
		county_name = "New York"
		county_name_use = "New+York"

	#Here we define the URL that the county's webpage is at, grab the page, and write it to a file. The writing to a file isn't strictly necessary, but speeds things up.

	file_name = tmpdir + county_name_use + "-NY-clerks.html"
	county_url = "http://www.elections.ny.gov:8080/plsql_browser/county_boards?county_in=" + county_name_use
	data = urllib.urlopen(county_url).read()
	output = open(file_name,"w")
	output.write(data)
	output.close()

	#This line is usually unnecessary, but is present so the previous lines can be commented out.


	print file_name
	data = open(file_name).read()

	county = data

	#Once we have the data, we start parsing.

	phone = dogcatcher.find_phone(phone_re, county)

	#The Authority name is uniform across counties.

	if county_name == "Westchester":
		fax = "914-995-3190, 914-995-7753"
		review = review + "b"
	else:
		fax = dogcatcher.find_phone(fax_re, county)

	official_name = official_name_re.findall(county)[0]
	if "<br>" in official_name.lower():
		print county
		print official_name
		sys.exit()

	first_name, last_name, review = dogcatcher.split_name(official_name, review)

	#This section finds the full address. After finding the address, it identifies a city/state/zip (csz) combination and a PO Box number if that exists.
    #It removes both the CSZ and the PO Address (if it exists) from the full address, leaving behind a street address with some garbage.
    #It then cleans up the street address and pulls the city, state, and zip out of the csz, and assigns them as appropriate to the street address and state.

	address = address_re.findall(county)[0]

	print address

	csz = csz_re.findall(address)[0]

	if po_re.findall(address):
		po_street = " ".join(po_re.findall(address)[0].replace("<br>","").strip(", ").split())

	street = address.replace(po_street,"").replace(csz,"").replace("<br>",", ").replace("<BR>",", ").replace("<Br>",", ")

	#Replacing all of the <brs> can leave more commas than we want behind; this cleans that up.

	for item in comma_re.findall(street):
		street = street.replace(item, ", ")

	street = " ".join(street.split()).strip(", ")

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

	print "_______________________________________________________"


	if county_name == "Genesee":
		po_street = "P.O. Box 284"

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

dogcatcher.output(result, voter_state, cdir)
