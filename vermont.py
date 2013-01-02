import sys
import mechanize
import re
import json
import time
import urllib
import dogcatcher
import HTMLParser
import os
import xlrd

h = HTMLParser.HTMLParser()

cdir = os.path.dirname(os.path.abspath(__file__)) + "/"

#acquiring the FIPs lists that are necessary later
fips_data_re = re.compile(".+?VT.+?\n")
fips_data = dogcatcher.make_fips_data(fips_data_re)
fips_numbers = dogcatcher.make_fips_numbers(fips_data)
fips_names = dogcatcher.make_fips_names(fips_data)

voter_state = "VT"
source = "State"

middle_name_re = re.compile("( [a-zA-z]\.)")

result = [("authority_name", "first_name", "last_name", "town_name", "county_name", "fips",
    "street", "city", "address_state", "zip_code",
    "po_street", "po_city", "po_state", "po_zip_code",
    "reg_authority_name", "reg_first", "reg_last",
    "reg_street", "reg_city", "reg_state", "reg_zip_code",
    "reg_po_street", "reg_po_city", "reg_po_state", "reg_po_zip_code",
    "reg_phone", "reg_fax", "reg_email", "reg_website", "reg_hours",
    "phone", "fax", "email", "website", "hours", "voter_state", "source", "review")]

#The following section grabs the spreadsheet and writes it to a file. (Writing it to a file isn't strictly necessary, but saves some time down the line.)

url = "http://vermont-elections.org/elections1/2012TCPublicList%201.2012.xls"
filename = cdir + "vermont-clerks.xls"

urllib.urlretrieve(url, filename)

#The desired data is on sheet 0 of the downloaded file.

data = xlrd.open_workbook(filename).sheet_by_index(0)

#Each county exists in a separate row in the source data, so this cycles through the data row by row.

for row in range(1, data.nrows):

	authority_name, first_name, last_name, county_name, town_name, fips, street, city, address_state, zip_code, po_street, po_city, po_state, po_zip_code, reg_authority_name, reg_first, reg_last, reg_street, reg_city, reg_state, reg_zip_code, reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code, reg_phone, reg_fax, reg_email, reg_website, reg_hours, phone, fax, email, website, hours, review = dogcatcher.begin(voter_state)

	#The authority name is consistent from county to county and not included in the data.

	#The data is arranged in a well-ordered table, so we can split each row into a list of items and use each of those items in a consistent way from row to row.
	#Since we can be fairly confident about the format of the data, I mostly skip using the dogcatcher functions.

	authority_name = "Town Clerk"

	town_name = " ".join(data.cell(row,0).value.split())
	county_name = " ".join(data.cell(row,1).value.split())

	first_name = " ".join(data.cell(row,2).value.split())
	for middle in middle_name_re.findall(first_name):
		first_name = first_name.replace(middle,"")
	if first_name == "Vacant":
		first_name = ""
	last_name = " ".join(data.cell(row,3).value.split())

	street = " ".join(data.cell(row,9).value.split())
	po_street = " ".join(data.cell(row,5).value.split())
	if po_street != street:
		po_city = " ".join(data.cell(row,6).value.split())
		po_state = " ".join(data.cell(row,7).value.split())
		po_zip_code = " ".join(data.cell(row,8).value.split())
	else:
		po_street = ""
	city = " ".join(data.cell(row,10).value.split())
	address_state = " ".join(data.cell(row,11).value.split())
	zip_code = " ".join(data.cell(row,12).value.split())

	if zip_code == "0542":
		zip_code = "05342"

	phone = dogcatcher.phone_clean(data.cell(row,13).value,"802")

	fax = dogcatcher.phone_clean(" ".join(data.cell(row,14).value.split()))
	if fax == "N/A":
		fax = ""

	email = " ".join(data.cell(row,15).value.lower().split())
	hours = data.cell(row,16).value.rstrip().replace("//","+++++")

	fips = dogcatcher.fips_find(county_name, fips_names, fips_numbers)
	
	result.append([authority_name, first_name, last_name, town_name, county_name, fips,
	street, city, address_state, zip_code,
	po_street, po_city,	po_state, po_zip_code,
	reg_authority_name, reg_first, reg_last,
	reg_street, reg_city, reg_state, reg_zip_code,
	reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code,
	reg_phone, reg_fax, reg_email, reg_website, reg_hours,
	phone, fax, email, website, hours, voter_state, source, review])

#This outputs the results to a separate text file.

output = open(cdir + "vermont.txt", "w")
for r in result:
	r = h.unescape(r)
	output.write("\t".join(r))
	output.write("\n")
output.close()