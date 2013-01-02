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
fips_data_re = re.compile(".+?SD.+?\n")
fips_data = dogcatcher.make_fips_data(fips_data_re)
fips_numbers = dogcatcher.make_fips_numbers(fips_data)
fips_names = dogcatcher.make_fips_names(fips_data)

voter_state = "SD"
source = "State"


result = [("authority_name", "first_name", "last_name", "county_name", "fips",
    "street", "city", "address_state", "zip_code",
    "po_street", "po_city", "po_state", "po_zip_code",
    "reg_authority_name", "reg_first", "reg_last",
    "reg_street", "reg_city", "reg_state", "reg_zip_code",
    "reg_po_street", "reg_po_city", "reg_po_state", "reg_po_zip_code",
    "reg_phone", "reg_fax", "reg_email", "reg_website", "reg_hours",
    "phone", "fax", "email", "website", "hours", "voter_state", "source", "review")]

#The following section grabs the website and writes it to a file. (Writing it to a file isn't strictly necessary, but saves some time down the line.)

file_path = cdir + "south_dakota-clerks.html"
url = "http://sdsos.gov/content/viewcontent.aspx?cat=elections&pg=/elections/auditorcontactinformation.shtm"

data = urllib.urlopen(url).read()
output = open(file_path,"w")
output.write(data)
output.close()


data = open(file_path).read()

data = data.replace("<br>","").replace("&nbsp;","").replace("<p>","")

county_data_re = re.compile("<tr vAlign=\"top\".+?</tr>", re.DOTALL)
county_item_re = re.compile("<td borderColor=.+?>\s*<.+?>(.+?)</font> *</td>", re.DOTALL)
email_re = re.compile("[^<>]+?@[^<>]+")

digit_re = re.compile("\d")
html_re = re.compile("<.+?>")

#print data

county_data = county_data_re.findall(data)

for county in county_data:

	authority_name, first_name, last_name, county_name, town_name, fips, street, city, address_state, zip_code, po_street, po_city, po_state, po_zip_code, reg_authority_name, reg_first, reg_last, reg_street, reg_city, reg_state, reg_zip_code, reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code, reg_phone, reg_fax, reg_email, reg_website, reg_hours, phone, fax, email, website, hours, review = dogcatcher.begin(voter_state)

	#The data is arranged in a well-ordered table, so we can split each row into a list of items and use each of those items in a consistent way from row to row.
	county_item = county_item_re.findall(county)

	fax = dogcatcher.phone_clean(county_item[7])

	email = dogcatcher.find_emails(email_re, county)

	#For each item in the county, we trim any spare HTML out of it to make it easier to process.
	for item in county_item:
		index = county_item.index(item)
		for html in html_re.findall(item):
			county_item.insert(index,item.replace(html,""))
			county_item.pop(index+1)

	county_name = county_item[0].title()

	first_name = " ".join(county_item[1].split())
	last_name = county_item[2]

	if first_name == "":
		last_name = ""

	#The address are split into well-ordered columns. We check for a PO Box, to know whether we have a mailing address or a physical address, and then pull the street, city, and zip out.

	if "PO Box" in county_item[3]:
		po_street = " ".join(county_item[3].split())
		po_city = " ".join(county_item[4].split())
		po_zip_code = county_item[5]
		po_state = "SD"
	else:
		street = " ".join(county_item[3].split())
		city = " ".join(county_item[4].split())
		zip_code = county_item[5]
		address_state = "SD"

	phone = dogcatcher.phone_clean(county_item[6])

	print "____________________________________"

	print county_item

	print "++++++++++++++++++++++++++++++++++++"

	print email

	fips = dogcatcher.fips_find(county_name, fips_names, fips_numbers)

	result.append([authority_name, first_name, last_name, county_name, fips,
	street, city, address_state, zip_code,
	po_street, po_city,	po_state, po_zip_code,
	reg_authority_name, reg_first, reg_last,
	reg_street, reg_city, reg_state, reg_zip_code,
	reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code,
	reg_phone, reg_fax, reg_email, reg_website, reg_hours,
	phone, fax, email, website, hours, voter_state, source, review])

#This outputs the results to a separate text file.

output = open(cdir + "south_dakota.txt", "w")
for r in result:
	r = h.unescape(r)
	output.write("\t".join(r))
	output.write("\n")
output.close()