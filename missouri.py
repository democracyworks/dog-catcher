import sys
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

#acquiring the FIPs lists that are necessary later
fips_data_re = re.compile(".+?MO.+?\n")
fips_data = dogcatcher.make_fips_data(fips_data_re)
fips_numbers = dogcatcher.make_fips_numbers(fips_data)
fips_names = dogcatcher.make_fips_names(fips_data)

voter_state = "MO"
source = "State"

county_result = [("authority_name", "first_name", "last_name", "county_name", "fips",
    "street", "city", "address_state", "zip_code",
    "po_street", "po_city", "po_state", "po_zip_code",
    "reg_authority_name", "reg_first", "reg_last",
    "reg_street", "reg_city", "reg_state", "reg_zip_code",
    "reg_po_street", "reg_po_city", "reg_po_state", "reg_po_zip_code",
    "reg_phone", "reg_fax", "reg_email", "reg_website", "reg_hours",
    "phone", "fax", "email", "website", "hours", "voter_state", "source", "review")]

city_result = [("authority_name", "first_name", "last_name", "town_name", "fips",
    "street", "city", "address_state", "zip_code",
    "po_street", "po_city", "po_state", "po_zip_code",
    "reg_authority_name", "reg_first", "reg_last",
    "reg_street", "reg_city", "reg_state", "reg_zip_code",
    "reg_po_street", "reg_po_city", "reg_po_state", "reg_po_zip_code",
    "reg_phone", "reg_fax", "reg_email", "reg_website", "reg_hours",
    "phone", "fax", "email", "website", "hours", "voter_state", "source", "review")]

county_list_re = re.compile("option value=\"(.+?)\">.+?<")

#Every county is a different item in a dropdown menu, so we have to cycle through them all.
#To do so, we grab the dropdown menu, extract a list of counties, then grab a series of web pages based on that list.
#This grabs a page containing a list of GA counties and writes it to a file. Writing it isn't strictly necessary, but saves some run time in the long run.

file_path = "C:\Users\pkoms\Documents\TurboVote\Scraping\missouri-counties.html"

url = "http://www.sos.mo.gov/elections/goVoteMissouri/localelectionauthority.aspx"
data = urllib.urlopen(url).read()
output = open(file_path,"w")
output.write(data)
output.close()

county_list = county_list_re.findall(data)

#This uses the mechanize package to submit every item in county_list--the list of county names as used in the menu--and grab a webpage based on each one.

trim_re = re.compile("resultset\">(.+?)</div>", re.DOTALL)

for county in county_list:

	br = mechanize.Browser() #Creates a mechanize browser object.
	br.set_handle_robots(False) # ignore robots
	br.open(url) #Opens the page.
	br.select_form(name = "form1") #The drop-down menu is titled form1.
	br["electioncounty"] = [county,] #It takes an input called CountyName.
	res = br.submit() #res is the resulting page when we submit the inputs from earlier
	content = res.read() #this creates a string of the page.
	trimmed_content = trim_re.findall(content)[0] #this trims the page down to only what we need.
	#This writes the page to a file.
	file_path = cdir + county + "-mo-clerks.html"
	output = open(file_path,"w")
	output.write(trimmed_content)
	output.close()

space_re = re.compile("[.a-z][A-Z]")
office_name_re = re.compile(">([^><]+?)<")
phone_re = re.compile("(\(\d{3}\).+?)<.+?(?=FAX)")
fax_re = re.compile("FAX .+?W", re.DOTALL)
website_re = re.compile(">(http://.+?)<")
html_re = re.compile("<.+?>", re.DOTALL)

po_re = re.compile("(P\.*O\.*.+?),")
csz_re = re.compile("[^,]+?, [A-Z]{2,2} [\d-]+")
city_re = re.compile("(.+?),")
state_re = re.compile("[A-Z]{2,2}")
zip_re = re.compile("\d{5}[\d-]*")

address_re = re.compile(".+?[A-Z]{2,2} \d{5}[\d-]*")


for county_title in county_list:


	authority_name, first_name, last_name, county_name, town_name, fips, street, city, address_state, zip_code, po_street, po_city, po_state, po_zip_code, reg_authority_name, reg_first, reg_last, reg_street, reg_city, reg_state, reg_zip_code, reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code, reg_phone, reg_fax, reg_email, reg_website, reg_hours, phone, fax, email, website, hours, review = dogcatcher.begin(voter_state)

	county_name = county_title

	file_path = cdir + county_name + "-mo-clerks.html"
	county = open(file_path).read().replace("&nbsp;"," ").replace("Post Office","P.O.").replace("Ste Genevieve","Ste. Genevieve")
	county = county.replace("\n","").replace("\r","")
	for item in space_re.findall(county_name):
		if "Mc" not in county_name:
			county_name = dogcatcher.insert(county_name," ",county_name.find(item)+1)
		if "De Kalb" in county_name:
			county_name = "DeKalb"

	authority_name = authority_name_re.findall(county)[0]

	county = county.replace(authority_name,"")#Removing as much as possible from the data makes it easier to find the address later.

	office_name = office_name.replace(county_name,"").replace("County","").strip()

	website = dogcatcher.website_find(website_re, county)
	phone = dogcatcher.phone_find(phone_re, county)
	fax = dogcatcher.phone_find(fax_re, county)

	for item in html_re.findall(county): #Removing as much as possible from the data makes it easier to find the address later.
		county = county.replace(item,", ").strip(", ")


	#This section finds the address. After finding the address, it identifies a city/state/zip (csz) combination and a PO Box number if that exists.
    #It removes both the CSZ and the PO Address (if it exists) from the full address, leaving behind a street address with some garbage.
    #It then cleans up the street address and pulls the city, state, and zip out of the csz, and assigns them as appropriate to the street address and state.

	print county

	address = address_re.findall(county)[0]
	print address

	csz = csz_re.findall(address)[0].strip()

	try:
		po_street = po_re.findall(address)[0]
	except:
		po_street = ""

	street = address.replace(po_street,"").replace(csz,"").replace("\n","")
	street = " ".join(street.replace(" ,",",").strip(" \n/,").split(" ")).strip(", ")

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


	if county_name == "Kansas City":
		fips = "999"
	elif county_name == "St. Louis City":
		fips = "510"
		county_name = "St. Louis"
	else:
		fips = dogcatcher.fips_find(county_name, fips_names, fips_numbers)


	if "City" not in county_name:
		county_result.append([authority_name, first_name, last_name, county_name, fips,
		street, city, address_state, zip_code,
		po_street, po_city, po_state, po_zip_code,
		reg_authority_name, reg_first, reg_last,
		reg_street, reg_city, reg_state, reg_zip_code,
		reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code,
		reg_phone, reg_fax, reg_email, reg_website, reg_hours,
		phone, fax, email, website, hours, voter_state, source, review])
	else:
		print county_name
		city_result.append([authority_name, first_name, last_name, town_name, county_name, fips,
		street, city, address_state, zip_code,
		po_street, po_city, po_state, po_zip_code,
		reg_authority_name, reg_first, reg_last,
		reg_street, reg_city, reg_state, reg_zip_code,
		reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code,
		reg_phone, reg_fax, reg_email, reg_website, reg_hours,
		phone, fax, email, website, hours, voter_state, source, review])

#This outputs the results to two separate text files: one for counties in MO, and one for cities.

output = open("C:\Users\pkoms\Documents\TurboVote\Scraping\missouri-counties.txt", "w")
for r in county_result:
	r = h.unescape(r)
	output.write("\t".join(r))
	output.write("\n")
output.close()

output = open("C:\Users\pkoms\Documents\TurboVote\Scraping\missouri-cities.txt", "w")
for r in city_result:
	r = h.unescape(r)
	output.write("\t".join(r))
	output.write("\n")
output.close()