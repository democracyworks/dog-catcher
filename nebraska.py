import urllib
import re
import sys
import dogcatcher
import HTMLParser
import os

h = HTMLParser.HTMLParser()

cdir = os.path.dirname(os.path.abspath(__file__)) + "/"

voter_state = "NE"
source = "State"


result = [("authority_name", "first_name", "last_name", "county_name", "fips",
    "street", "city", "address_state", "zip_code",
    "po_street", "po_city", "po_state", "po_zip_code",
    "reg_authority_name", "reg_first", "reg_last",
    "reg_street", "reg_city", "reg_state", "reg_zip_code",
    "reg_po_street", "reg_po_city", "reg_po_state", "reg_po_zip_code",
    "reg_phone", "reg_fax", "reg_email", "reg_website", "reg_hours",
    "phone", "fax", "email", "website", "hours", "voter_state", "source", "review")]

file_path = cdir + "nebraska-clerks.html"
url = "http://www.sos.ne.gov/elec/clerks.html"

data = urllib.urlopen(url).read()
output = open(file_path,"w")
output.write(data)
output.close()

data = open(file_path).read()

data = data.replace("</span>","")

county_re = re.compile("<div style=\"width: 340px.+?>(.+?)</div>", re.DOTALL)
phone_re = re.compile("Phone Number: (.+?) *<")
fax_re = re.compile("Fax Number: (.+?) *<")
email_re = re.compile("mailto:(.+?)\"")

address_re = re.compile("Address: (.+?)<")
city_re = re.compile("City: (.+)")
zip_re = re.compile("Zip Code: (.+?)<")

name_re = re.compile("Name: (.+?)<")
title_re = re.compile("\(.+?\)")

county_name_re = re.compile("County: (.+?) \(")

county_data = county_re.findall(data)

for county in county_data:
	print "________________________________________________"
	#print county

	authority_name, first_name, last_name, county_name, town_name, fips, street, city, address_state, zip_code, po_street, po_city, po_state, po_zip_code, reg_authority_name, reg_first, reg_last, reg_street, reg_city, reg_state, reg_zip_code, reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code, reg_phone, reg_fax, reg_email, reg_website, reg_hours, phone, fax, email, website, hours, review = dogcatcher.begin(voter_state)

	county_name = county_name_re.findall(county)[0]

	name = name_re.findall(county)[0].strip()

	title = title_re.findall(name)
	if title:
		official_name = name.replace(title[0],"")
	else:
		official_name = name

	first_name, last_name, review = dogcatcher.split_name(official_name, review)

	authority_name = "Election Commissioner"

	print name
	print first_name

	#There's only a single physical or mailing address, and all addresses are only two lines. State is not included.
	#Address_re finds the address. We then check whether it's a physical or mailing address, and assign the other variables accordingly.
	#Since the city and zip code are explicitly set out in the data (as City: Foovile \n Zip: 11111), this gets both directly from the county data, instead of extracting it from the complete address.
	
	address = address_re.findall(county)[0].strip()

	if "PO " in address:
		po_street = address
		po_city = city_re.findall(county)[0].strip()
		po_zip_code = zip_re.findall(county)[0].strip()
	else:
		street = address
		city = city_re.findall(county)[0].strip()
		zip_code = zip_re.findall(county)[0].strip()

	email = dogcatcher.find_emails(email_re, county).replace("%20","")

	phone = dogcatcher.phone_find(phone_re, county)

	fax = dogcatcher.phone_find(fax_re, county)

	fips = dogcatcher.fips_find(county_name, voter_state)

	result.append([authority_name, first_name, last_name, county_name, fips,
	street, city, address_state, zip_code,
	po_street, po_city,	po_state, po_zip_code,
	reg_authority_name, reg_first, reg_last,
	reg_street, reg_city, reg_state, reg_zip_code,
	reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code,
	reg_phone, reg_fax, reg_email, reg_website, reg_hours,
	phone, fax, email, website, hours, voter_state, source, review])

#This outputs the results to a separate text file.

output = open(cdir + "nebraska.txt", "w")
for r in result:
	output.write("\t".join(r))
	output.write("\n")
output.close()