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

voter_state = "TN"
source = "State"


result = [("authory_name", "first_name", "last_name", "county_name", "fips",
    "street", "city", "address_state", "zip_code",
    "po_street", "po_city", "po_state", "po_zip_code",
    "reg_authority_name", "reg_first", "reg_last",
    "reg_street", "reg_city", "reg_state", "reg_zip_code",
    "reg_po_street", "reg_po_city", "reg_po_state", "reg_po_zip_code",
    "reg_phone", "reg_fax", "reg_email", "reg_website", "reg_hours",
    "phone", "fax", "email", "website", "hours", "voter_state", "source", "review")]

#Every county is on a different webpage so we have to cycle through them all.
#To do so, we go elsewhere, extract a list of counties, then later grab a series of web pages based on that list.
#(Writing it to a file isn't strictly necessary, but saves some time down the line.)

file_path = cdir + "tennessee-counties.html"
url = "http://www.tdot.state.tn.us/longrange/countylist.htm"
data = urllib.urlopen(url).read()
output = open(file_path,"w")
output.write(data)
output.close()

data = open(file_path).read()

county_name_re = re.compile(">\d{2} (.+?)<")

county_data_re = re.compile("<td colspan=\"2\"><div class=\"title\">.+?</table>", re.DOTALL)

website_re = re.compile("a href='(http://[^'].+?)'")
email_re = re.compile("a href='mailto:(.+?)'")

phone_re = re.compile("Phone: .+?(\d{3}.+?)<", re.DOTALL)
fax_re = re.compile("Fax: .+?(\d{3}.+?)<", re.DOTALL)

name_re = re.compile("Administrator:.+?top\">(.+?)<",re.DOTALL)

mailing_address_re = re.compile("Mailing Address:.+?top\"(>.+?<)/td>",re.DOTALL)
po_re = re.compile(">(.+?)<")

address_re = re.compile(">Address:.+?top\">(.+?\d{5}[\d-]*) <br /></td>", re.DOTALL)
multi_space_re = re.compile("  +")
newline_re = re.compile("[\s][\s]+")

city_zip_re = re.compile("([^<>]+?<br />[\s]+?\d{5}[\d-]*)[\s]+",re.DOTALL)
city_re = re.compile("(.+?)<")

zip_re = re.compile(">[\s]+?(\d{5}[\d-]*)")

hours_re = re.compile("Hours: <.+?top\">(.+?)<",re.DOTALL)

county_names = county_name_re.findall(data)

for county_id in county_names:

	authority_name, first_name, last_name, county_name, town_name, fips, street, city, address_state, zip_code, po_street, po_city, po_state, po_zip_code, reg_authority_name, reg_first, reg_last, reg_street, reg_city, reg_state, reg_zip_code, reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code, reg_phone, reg_fax, reg_email, reg_website, reg_hours, phone, fax, email, website, hours, review = dogcatcher.begin(voter_state)

	#The URLs are uniformly formatted; we insert every county on the list of county names into the URL format, and then grab and save a webpage based on that.
	#(Writing it to a file isn't strictly necessary, but saves some time down the line.)

	file_name = cdir + county_id + "-TN-clerks.html"
	county_url = "http://tnsos.org/elections/election_commissions.php?County=" + county_id

	data = urllib.urlopen(county_url).read()
	output = open(file_name,"w")
	output.write(data)
	output.close()

	county_name = county_id

	data = open(file_name).read()
	county = county_data_re.findall(data)[0]


	website = dogcatcher.find_website(website_re, county)
	email = dogcatcher.find_emails(email_re, county)

	phone = dogcatcher.find_phone(phone_re, county)
	fax = dogcatcher.find_phone(fax_re, county)


	hours = hours_re.findall(county)[0].strip()


	official_name = name_re.findall(county)[0]
	first_name, last_name, review = dogcatcher.split_name(official_name, review)

	authority_name = "County Election Commission"

	#Every county has an address; some have separately designated mailing addresses. We first break down the address and extract the data out of it.
	#It then checks whether there's a mailing address, and if so, extracts all of the data out of it.

	address = address_re.findall(county)[0]
	city_zip = city_zip_re.findall(county)[0]

	city = city_re.findall(city_zip)[0].strip()
	zip_code = zip_re.findall(city_zip)[0]
	street = address.replace(city_zip,"").replace("<br />","").strip("\n ,")

	for space in multi_space_re.findall(street):
		street = street.replace(space," ",1)
	for line in newline_re.findall(street):
		street = street.replace(line,", ",1)

	if "Mailing Address" in county:
		mailing_address = mailing_address_re.findall(county)[0]
		po_street = po_re.findall(mailing_address)[0].strip()
		po_city = city
		po_zip_code = zip_re.findall(mailing_address)[0]


	fips = dogcatcher.find_fips(county_name, voter_state)

	result.append([authority_name, first_name, last_name, county_name, fips,
	street, city, address_state, zip_code,
	po_street, po_city,	po_state, po_zip_code,
	reg_authority_name, reg_first, reg_last,
	reg_street, reg_city, reg_state, reg_zip_code,
	reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code,
	reg_phone, reg_fax, reg_email, reg_website, reg_hours,
	phone, fax, email, website, hours, voter_state, source, review])

#This outputs the results to a separate text file.

output = open(cdir + "tennessee.txt", "w")
for r in result:
	r = h.unescape(r)
	output.write("\t".join(r))
	output.write("\n")
output.close()