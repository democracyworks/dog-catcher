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
tmpdir = cdir + "tmp/"

voter_state = "OR"
source = "State"

#The following section grabs the website and writes it to a file. (Writing it to a file isn't strictly necessary, but saves some time down the line.)

url = "http://oregonvotes.org/pages/voterresources/clerk.html"
file_path = tmpdir + "oregon-clerks.html"

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

county_data_re = re.compile("<a[^\n]+?NAME=.+?</span>", re.DOTALL)
county_name_re = re.compile("NAME=\"(.+?)\"")

official_name_re = re.compile("<span>(.+?) *<br />", re.DOTALL)

email_re = re.compile("mailto:(.+?)\"")
website_re = re.compile("href=\"(.+?)\"")

phone_re = re.compile("[\nr] *([\d (),Ext\.-]+?)[/o<]")
fax_re = re.compile("Fax .+?[/\n]")

#phone_re = re.compile("[>r][^<]+?\(([\d-]+?[\) -]+\d{3}-\d{4}.*?)[oT]", re.DOTALL)

address_item_re = re.compile("([^<>\r\n]+?\d[^<>\r\n]+?)<br />")

state_re = re.compile(" ([A-Z][A-Z]) ")
city_re = re.compile("(.+?),")
zip_re = re.compile("\d{5}[\d-]*")

authority_name_re = re.compile("<span>.+? *<br />\s+(.+?)<", re.DOTALL)


data = data.replace("\t", "")
#fixing a known error in Coos county
data = data.replace("(54)396-3121","(541) 396-3121")
#data = data.replace("/ TTY","<br /> \nTTY")
data = data.replace("</a> \r\n<br />","</a> <br />")
data = data.replace("&quot;","\"")
data = data.replace("PO Box 6005\r\n<br />","PO Box 6005<br />")

county_data = county_data_re.findall(data)

for county in county_data:

	authority_name, first_name, last_name, county_name, town_name, fips, street, city, address_state, zip_code, po_street, po_city, po_state, po_zip_code, reg_authority_name, reg_first, reg_last, reg_street, reg_city, reg_state, reg_zip_code, reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code, reg_phone, reg_fax, reg_email, reg_website, reg_hours, phone, fax, email, website, hours, review = dogcatcher.begin(voter_state)

	county_name = county_name_re.findall(county)[0].title()

	official_name = official_name_re.findall(county)[0].replace("\n","")

	first_name, last_name, review = dogcatcher.split_name(official_name, review)


	authority_name = authority_name_re.findall(county)[0].replace(county_name,"").strip()

	if county_name == "Clatsop":
		official_name = ""
		authority_name = "County Clerk"

	#print [county]

	phone = dogcatcher.find_phone(phone_re, county)

	fax = dogcatcher.find_phone(fax_re, county)

	email = dogcatcher.find_emails(email_re, county)

	website = dogcatcher.find_website(website_re, county)

	#There is only one address in any town, which is either a PO box or physical address.
	#It can be easily split into two lines, one with the street component and the other with the city, state, and zip.
	#This grabs the address, splits it, determines which it is by checking for the string "PO " in the first line, and acts accordingly.

	address_item = address_item_re.findall(county)

	if "PO " in address_item[0]:
		po_street = address_item[0].strip()
		po_city = city_re.findall(address_item[1])[0]
		po_state = state_re.findall(address_item[1])[0]
		po_zip_code = zip_re.findall(address_item[1])[0]
	else:
		street = address_item[0].strip()
		city = city_re.findall(address_item[1])[0]
		state = state_re.findall(address_item[1])[0]
		zip_code = zip_re.findall(address_item[1])[0]

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
dogcatcher.output(result, voter_state, cdir)
