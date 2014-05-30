import urllib
import re
import dogcatcher
import HTMLParser
import os

h = HTMLParser.HTMLParser()

cdir = os.path.dirname(os.path.abspath(__file__)) + "/"
tmpdir = cdir + "tmp/"

#The following section grabs the website and writes it to a file. (Writing it to a file isn't strictly necessary, but saves some time down the line.)

file_path = tmpdir + "washington-clerks.html"
url = "http://www.sos.wa.gov/elections/viewauditors.aspx"

voter_state = "WA"
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

data = data.replace("<br>","<br>\n").replace("<br/>","<br/>\n")

county_re = re.compile("<div class=\"panel-body\">(.+?)</div>", re.DOTALL)
county_name_re = re.compile("<h2 class=\"reset-margin\">(.+?) County</h2>")

email_re = re.compile("mailto:(.+?)\"")
website_re = re.compile("target=\"_blank\">(.+?)<")

phone_re = re.compile("Ph.+?> *(\d{3}-\d{3}-\d{4}.*?) *<")
fax_re = re.compile("Fa.+?> *(\d{3}-\d{3}-\d{4}.*?) *<")

county_data = county_re.findall(data)
county_names = county_name_re.findall(data)

address_re = re.compile("Address: </b><p>(.+?)</p><b>Phone", re.DOTALL)
csz_re = re.compile(" *([^,\n]+?, [A-Z][A-Z] *\d{5}[\d-]*)")
city_re = re.compile("(.+?),")
state_re = re.compile(" ([A-Z][A-Z]) ")
zip_re = re.compile(" (\d{5}[\d-]*)")
po_re = re.compile("(PO Box .+?)<br")

print county_names
print county_data

for idx, county in enumerate(county_data):

	authority_name, first_name, last_name, county_name, town_name, fips, street, city, address_state, zip_code, po_street, po_city, po_state, po_zip_code, reg_authority_name, reg_first, reg_last, reg_street, reg_city, reg_state, reg_zip_code, reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code, reg_phone, reg_fax, reg_email, reg_website, reg_hours, phone, fax, email, website, hours, review = dogcatcher.begin(voter_state)

	county_name = county_names[idx]
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

	street = address.replace(po_street,"").replace(csz,"").replace("</b><p>","")
	street = street.replace("<br>",", ").replace("<br />",", ").replace("\n",", ").replace(" ,",",").strip(" \n/,")

	print po_street

	if po_street:
		po_city = city_re.findall(csz)[0]
		po_state = state_re.findall(csz)[0]
		po_zip_code = zip_re.findall(csz)[0]
	if street:
		city = city_re.findall(csz)[0]
		address_state = state_re.findall(csz)[0]
		zip_code = zip_re.findall(csz)[0]

	print street + " / " + po_street
	print zip_code + po_zip_code

	print "----------------------------------------------------------"

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
