import mechanize
import re
import json
import time
import urllib
import dogcatcher
import HTMLParser
import os

h = HTMLParser.HTMLParser()

cdir = os.path.dirname(os.path.abspath(__file__)) + "/"

voter_state = "IL"
source = "State"

city_result = [("authority_name", "first_name", "last_name", "town_name", "county_name", "fips",
    "street", "city", "address_state", "zip_code",
    "po_street", "po_city", "po_state", "po_zip_code",
    "reg_authority_name", "reg_first", "reg_last",
    "reg_street", "reg_city", "reg_state", "reg_zip_code",
    "reg_po_street", "reg_po_city", "reg_po_state", "reg_po_zip_code",
    "reg_phone", "reg_fax", "reg_email", "reg_website", "reg_hours",
    "phone", "fax", "email", "website", "hours", "voter_state", "source", "review")]

county_result = [("authority_name", "first_name", "last_name", "county_name", "fips",
    "street", "city", "address_state", "zip_code",
    "po_street", "po_city", "po_state", "po_zip_code",
    "reg_authority_name", "reg_first", "reg_last",
    "reg_street", "reg_city", "reg_state", "reg_zip_code",
    "reg_po_street", "reg_po_city", "reg_po_state", "reg_po_zip_code",
    "reg_phone", "reg_fax", "reg_email", "reg_website", "reg_hours",
    "phone", "fax", "email", "website", "hours", "voter_state", "source", "review")]


#The following section grabs the website and writes it to a file using the Mechanize package. (Writing it to a file isn't strictly necessary, but saves some time down the line.)
#The website is hidden behind a drop-down menu; there's an "All" option on that menu, so we select it and grab the entire page. That page should have all the data we need.

url = "http://www.elections.il.gov/ElectionAuthorities/ElecAuthorityList.aspx"

br = mechanize.Browser()
br.set_handle_robots(False) # ignore robots
br.open(url)
br.select_form(name = "aspnetForm")
br["ctl00$ContentPlaceHolder1$ddlCounty"] = ["All",]
res = br.submit()
content = res.read()
file_path = cdir + "illinois-clerks.html"
output = open(file_path,"w")
output.write(content)
output.close()

data = open(file_path).read()

county_data_re = re.compile("<tr>\s+<td class=\"tdJurisdictions(.+?)</tr>", re.DOTALL)
county_name_re = re.compile(">([^<]+?)</[as][pan]*>")

website_re = re.compile("href= (.+?) ")
email_re = re.compile("mailto:(.+?)\"")

phone_re = re.compile("(\d{3}/\d{3}-.+?)<.+?>\d{3}/\d{3}-.+?<")

fax_re = re.compile("\d{3}/\d{3}-.+?<.+?>(\d{3}/\d{3}-.+?)<")

office_name_re = re.compile("thTitle\"><span>(.+?)<")
name_re = re.compile("thName\"><.+?>(.+?)<")

address_re = re.compile("thAddress\"><span>(.+?)</span>")
csz_re = re.compile("([^>,\n]+?, [A-Z][A-Z] *\d{5}[\d-]*)")
city_re = re.compile("(.+?), [A-Z][A-Z]")
state_re = re.compile(" ([A-Z][A-Z]) ")
zip_re = re.compile(" (\d{5}[\d-]*)")
po_re = re.compile("(P[\. ]*O\. BOX .+?)<", re.DOTALL)

county_data = county_data_re.findall(data)

for county in county_data:
	print "+++++++++++++++++++++++++++++++++++++++++++"
	print county
	print "--------------------------------------------"

	authority_name, first_name, last_name, county_name, town_name, fips, street, city, address_state, zip_code, po_street, po_city, po_state, po_zip_code, reg_authority_name, reg_first, reg_last, reg_street, reg_city, reg_state, reg_zip_code, reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code, reg_phone, reg_fax, reg_email, reg_website, reg_hours, phone, fax, email, website, hours, review = dogcatcher.begin(voter_state)

	county_name = county_name_re.findall(county)[0].title().replace("Dekalb","DeKalb").replace("Dewitt","De Witt").replace("Dupage","DuPage").replace("Jodaviess","Jo Daviess")
	county_name = county_name.replace("Lasalle","LaSalle").replace("Mcd","McD").replace("Mcl","McL").replace("Mch","McH")
	
	authority_name = office_name_re.findall(county)[0].strip().title()
	official_name = name_re.findall(county)[0].strip()
	first_name, last_name, review = dogcatcher.split_name(official_name, review)

	if "City Of" in county_name:
		town_name = county_name.replace("City Of ","")
		county_name = ""

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

	street = address.replace(po_street,"").replace(csz,"").replace("<br />",", ")
	street = street.replace("\n",", ").replace("\r","").replace(" ,",",").strip(" \n/,")

	if po_street:
		po_city = city_re.findall(csz)[0].strip()
		po_state = state_re.findall(csz)[0].strip()
		po_zip_code = zip_re.findall(csz)[0].strip()
	if street:
		city = city_re.findall(csz)[0].strip()
		address_state = state_re.findall(csz)[0].strip()
		zip_code = zip_re.findall(csz)[0].strip()

	if county_name:

		fips = dogcatcher.find_fips(county_name, voter_state)

		county_result.append([authority_name, first_name, last_name, county_name, fips,
			street, city, address_state, zip_code,
			po_street, po_city, po_state, po_zip_code,
			reg_authority_name, reg_first, reg_last,
			reg_street, reg_city, reg_state, reg_zip_code,
			reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code,
			reg_phone, reg_fax, reg_email, reg_website, reg_hours,
			phone, fax, email, website, hours, voter_state, source, review])

	else:

		if street:
			fips, county_name = dogcatcher.map_fips(city, address_state, zip_code)
		else:
			fips, county_name = dogcatcher.map_fips(po_city, po_state, po_zip_code)

		city_result.append([authority_name, first_name, last_name, town_name, county_name, fips,
			street, city, address_state, zip_code,
			po_street, po_city, po_state, po_zip_code,
			reg_authority_name, reg_first, reg_last,
			reg_street, reg_city, reg_state, reg_zip_code,
			reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code,
			reg_phone, reg_fax, reg_email, reg_website, reg_hours,
			phone, fax, email, website, hours, voter_state, source, review])


#This outputs the results to two separate text files: one for counties in IL, and one for cities.

output = open(cdir+ "illinois-counties.txt", "w")
for r in county_result:
	r = h.unescape(r)
	output.write("\t".join(r))
	output.write("\n")
output.close()

output = open(cdir + "illinois-cities.txt", "w")
for r in city_result:
    r = h.unescape(r)
    output.write("\t".join(r))
    output.write("\n")
output.close()