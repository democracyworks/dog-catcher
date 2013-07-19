import urllib
import re
import sys
import dogcatcher
import HTMLParser
import os

h = HTMLParser.HTMLParser()

cdir = os.path.dirname(os.path.abspath(__file__)) + "/"

voter_state = "NJ"
source = "state"

result = [("authority_name", "first_name", "last_name", "county_name", "fips",
    "street", "city", "address_state", "zip_code",
    "po_street", "po_city", "po_state", "po_zip_code",
    "reg_authority_name", "reg_first", "reg_last",
    "reg_street", "reg_city", "reg_state", "reg_zip_code",
    "reg_po_street", "reg_po_city", "reg_po_state", "reg_po_zip_code",
    "reg_phone", "reg_fax", "reg_email", "reg_website", "reg_hours",
    "phone", "fax", "email", "website", "hours", "voter_state", "source", "review")]

#The following section grabs the website and writes it to a file. (Writing it to a file isn't strictly necessary, but saves some time down the line.)

file_path = cdir + "new_jersey-clerks.txt"
url = "http://www.nj.gov/state/elections/voting-information-local-officials.html"

data = urllib.urlopen(url).read()
output = open(file_path, "w")
output.write(data)
output.close()

data = open(file_path).read()

county_data_re = re.compile("\n<div id=\"county\">(.+?)</div>\n</div>", re.DOTALL)
county_name_re = re.compile(">([^\n<>]+?)<")
clerk_re = re.compile("(County Clerk.+?</div>)", re.DOTALL)
registrar_re = re.compile("County Clerk.+?</div>(.+?</div>)", re.DOTALL)

name_re = re.compile("</strong><br /> *\n\s*([^\d]+?)<", re.DOTALL)
name_2_re = re.compile("(.+?),")

phone_re = re.compile("<strong>(\d{3}-\d{3}-\d{4}.*?) *</strong>")
fax_re = re.compile("\(*FAX\)* (\d{3}-\d{3}-\d{4}.*?)<br")
hours_re = re.compile("Office Hours: *(.+?pm)<[br]*[/div]*",re.DOTALL)
website_re = re.compile("<a href=\"(.+?)\">")

address_re = re.compile("</strong><br />(.+?)<strong>", re.DOTALL)
comma_fix_re = re.compile("\n[ ,\t]*\n")
po_re = re.compile("(P\.*O\.*.+?),")
state_re = re.compile(" ([A-Z][A-Z]) ")
csz_re = re.compile("[^,\t\n]+?, [A-Z][A-Z] \d{5}[\d-]*")
city_re = re.compile("(.+?),")
zip_re = re.compile("\d{5}[\d-]*")
is_street_re = re.compile("[^,\. \n\t]")
street_break_re = re.compile(" *,* *\n")
multi_comma_re = re.compile(", *, *")
multi_space_re = re.compile("  +")

data = data.replace("- ","-")
data = data.replace(" and<br>\n",", ")
#fixing an edge case in Morris County
data = data.replace("-4:30pm","-4:30pm<br")
#fixing an edge case in Mercer County
data = data.replace("(FAX) 609-989-6888<br>\nOffice Hours: 8:00am-4:00pm","(FAX) 609-989-6888<br>\nOffice Hours: 8:00am-4:00pm<br>")
data = dogcatcher.po_standardize(data)

county_data = county_data_re.findall(data)

#In each county, there are separate offices for registration and absentee ballots. This separates those offices and then applies essentially identical procedures to both.
for county in county_data:
	authority_name, first_name, last_name, county_name, town_name, fips, street, city, address_state, zip_code, po_street, po_city, po_state, po_zip_code, reg_authority_name, reg_first, reg_last, reg_street, reg_city, reg_state, reg_zip_code, reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code, reg_phone, reg_fax, reg_email, reg_website, reg_hours, phone, fax, email, website, hours, review = dogcatcher.begin(voter_state)


	county_name = county_name_re.findall(county)[0]

	#This isolates the county clerk data from the complete county.
	clerk = clerk_re.findall(county)[0]

	clerk_name = name_re.findall(clerk)[0]	
	first_name, last_name, review = dogcatcher.split_name(clerk_name, review)

	phone = dogcatcher.find_phone(phone_re, clerk)

	fax = dogcatcher.find_phone(fax_re, clerk)

	website = dogcatcher.find_website(website_re, clerk)

	hours = " ".join(hours_re.findall(clerk)[0].replace("<br>\n"," ").split())

	#It's hard to get the address without also getting the clerk's name.
	#So we first find the address, remove the clerk's name, and clean up a few html tags.
	#That can leave a mess of commas, so we clean that up.
	#We then extract the City, State, and Zip (CSZ) and check for a PO Box.
	#We then remove the CSZ and PO box from the address to form the street, and check whether it exists.
	#We then check whether there's anything left to be a street address. If there is, we clean it and trim it down to one line.
	#Based on whether there's a street address and a PO Box at this point, we assign the city, state, and zip accordingly.


	address = address_re.findall(clerk)[0].replace(clerk_name,"").replace("<br>",", ")
	address = address.replace("</b>","").replace("<br />","").replace("</font>","")
	for item in comma_fix_re.findall(address):
		address = address.replace(item,"")
	csz = csz_re.findall(address)[0].strip()

	if po_re.findall(address):
		po_street = po_re.findall(address)[0]

	street = " ".join(address.replace(csz,"").replace(po_street,"").rstrip(", ").replace("\t","").split(" ")).strip(", .\n\t")

	if street:
		while street_break_re.findall(street):
			for lbreak in street_break_re.findall(street):
				street = street.replace(lbreak,", ")
		while multi_space_re.findall(street):
			for multi in multi_space_re.findall(street):
				street = street.replace(multi," ")

		street = street.replace(", , ",", ").replace(",,",",")
		city = city_re.findall(csz)[0]
		address_state = state_re.findall(csz)[0]
		zip_code = zip_re.findall(csz)[0]
		if po_street:
			po_city = city_re.findall(csz)[0]
			po_state = state_re.findall(csz)[0]
			po_zip_code = zip_re.findall(csz)[0]
	else:
		po_city = city_re.findall(csz)[0]
		po_state = state_re.findall(csz)[0]
		po_zip_code = zip_re.findall(csz)[0]

	#This isolates the registrar data from the complete county.
	registrar = registrar_re.findall(county)[0]

	if name_re.findall(registrar):
		registrar_name = name_re.findall(registrar)[0]
		reg_first, reg_last, review = dogcatcher.split_name(registrar_name, review)
	else:
		reg_first = ""
		reg_last = ""

	reg_phone = dogcatcher.find_phone(phone_re, registrar)

	reg_fax = dogcatcher.find_phone(fax_re, registrar)

	reg_phone = reg_phone.replace("201-336-7073", "201-336-7000")

	website = dogcatcher.find_website(website_re, registrar)

	reg_hours = " ".join(hours_re.findall(registrar)[0].replace("<br>\n"," ").split())

	#It's hard to get the address without also getting the registrar's name.
	#So we first find the address, remove the registrar's name, and clean up a few html tags.
	#That can leave a mess of commas, so we clean that up.
	#We then extract the City, State, and Zip (CSZ) and check for a PO Box.
	#We then remove the CSZ and PO box from the address to form the street address, and check whether it exists.
	#If it does, we clean it and trim it down to one line.
	#Based on whether there's a street address and a PO Box at this point, we assign the city, state, and zip accordingly.

	address = address_re.findall(registrar)[0].replace(registrar_name,"").replace("<br>",", ")

	address = address.replace("</b>","").replace("<br />","").replace("</font>","").replace("\t","")

	for item in comma_fix_re.findall(address):
		address = address.replace(item,"")

	print "__________________________"

	csz = csz_re.findall(address)[0].strip("\t ")
	try:
		reg_po_street = po_re.findall(address)[0]
	except:
		print county_name

	reg_street = " ".join(address.replace(csz,"").replace(reg_po_street,"").rstrip(", ").replace("\t","").split(" ")).strip(", .\n\t")

	print [address]
	print [csz]
	print [reg_street]

	if reg_street:

		while street_break_re.findall(reg_street):
			for lbreak in street_break_re.findall(reg_street):
				reg_street = reg_street.replace(lbreak,", ")
		while multi_space_re.findall(reg_street):
			for multi in multi_space_re.findall(reg_street):
				reg_street = reg_street.replace(multi," ")

		reg_street = reg_street.replace(", , ",", ").replace(",,",",")
		reg_city = city_re.findall(csz)[0]
		reg_state = state_re.findall(csz)[0]
		reg_zip_code = zip_re.findall(csz)[0]

		if reg_po_street:
			reg_po_city = city_re.findall(csz)[0]
			reg_po_state = state_re.findall(csz)[0]
			reg_po_zip_code = zip_re.findall(csz)[0]
	else:
		reg_po_city = city_re.findall(csz)[0]
		reg_po_state = state_re.findall(csz)[0]
		reg_po_zip_code = zip_re.findall(csz)[0]

	print reg_street

	authority_name = "County Clerk"

	if "Commissioner" in county:
		reg_authority_name = "Commissioner of Registrations"
	else:
		reg_authority_name = "Superintendent of Elections"

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