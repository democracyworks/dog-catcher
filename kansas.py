import urllib
import re
import sys
import dogcatcher
import HTMLParser
import os

h = HTMLParser.HTMLParser()

cdir = os.path.dirname(os.path.abspath(__file__)) + "/"

#The following section grabs the website and writes it to a file. (Writing it to a file isn't strictly necessary, but saves some time down the line.)

file_path = cdir + "kansas-clerks.html"
url = "http://www.kssos.org/elections/elections_registration_ceo_display.aspx"

data = urllib.urlopen(url).read()
output = open(file_path,"w")
output.write(data)
output.close()

voter_state = "KS"
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

county_data_re = re.compile("<tr bgcolor=\"White.+?<td align=\"center\" nowrap=\"nowrap\">.+?</tr>", re.DOTALL)
county_item_re = re.compile("<font color=\".+?\">(.+?)</font>")

middle_name_re = re.compile(" ([a-zA-z]\.* )")
digit_re = re.compile("\d")

county_data = county_data_re.findall(data)


for county in county_data:

	authority_name, first_name, last_name, county_name, town_name, fips, street, city, address_state, zip_code, po_street, po_city, po_state, po_zip_code, reg_authority_name, reg_first, reg_last, reg_street, reg_city, reg_state, reg_zip_code, reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code, reg_phone, reg_fax, reg_email, reg_website, reg_hours, phone, fax, email, website, hours, review = dogcatcher.begin(voter_state)

	authority_name = "County Election Officer"

	# print "-------------------------------------------"
	# print county

	#The data is arranged in a well-ordered table, so we can split each row into a list of items and use each of those items in a consistent way from row to row.
	#Since we can be fairly confident about the format of the data, I mostly skip using the dogcatcher functions.
	county_item = county_item_re.findall(county)
	# print "+++++++++++++++++++++++++++++++++++++++++++"

	county_name = county_item[0].title().strip()

	official_name = county_item[1]
	first_name, last_name, review = dogcatcher.split_name(official_name, review)

	email = county_item[2].strip().lower()
	hours = county_item[3].strip()
	phone = dogcatcher.phone_clean(county_item[4])
	fax = dogcatcher.phone_clean(county_item[5])


	#Line 1 of the street address, Line 2 (if it exists), the city, state, and zip, are all distinct items in the array.
	#If there's a PO Box, it's always in Line 1.
	#This first checks for whether there's a PO box in Line 1. If there is, it creates po_city, po_state, and po_zip_code, and turns Line 1 into po_street, and checks whether Line 2 is a separate address.
	#If so, it creates street out of Line 2. Otherwise, it appends Line 2 to po_street.
	#If there isn't a PO Box, it checks whether there's a Line 2, and appends it to Line 1 to create street if it does. (If not, it just takes Line 1 as street.)
	#If street exists, it then creates city, address_state, and zip_code.

	address_1 = county_item[6].strip()
	address_2 = county_item[7].strip()

	if "PO Box" in address_1:
		po_city = county_item[8].strip()
		po_state = county_item[9].strip()
		po_zip_code = county_item[10].strip()
		if address_2:
			if digit_re.findall(address_2):
				street = address_2
			else:
				po_street = address_1 + ", " + address_2
		else:
			po_street = address_1
	else:
		if address_2:
			street = address_1 + ", " + address_2
		else:
			street = address_1
	if street:
		city = county_item[8].strip()
		address_state = county_item[9].strip()
		zip_code = county_item[10].strip()

	print street + " / " + po_street
	print city + " / " + po_city
	print address_state + " / " + po_state

	fips = dogcatcher.fips_find(county_name, voter_state)

	result.append([authority_name, first_name, last_name, county_name, fips,
		street, city, address_state, zip_code,
		po_street, po_city, po_state, po_zip_code,
		reg_authority_name, reg_first, reg_last,
		reg_street, reg_city, reg_state, reg_zip_code,
		reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code,
		reg_phone, reg_fax, reg_email, reg_website, reg_hours,
		phone, fax, email, website, hours, voter_state, source, review])

#This outputs the results to a separate text file.

output = open(cdir + "kansas.txt", "w")
for r in result:
	r = h.unescape(r)
	output.write("\t".join(r))
	output.write("\n")
output.close()