import os
import urllib
import re
import sys
import xlrd
import dogcatcher
import HTMLParser

h = HTMLParser.HTMLParser()
cdir = os.path.dirname(os.path.abspath(__file__)) + "/"

voter_state = "FL"
source = "State"

result = [("authority_name", "first_name", "last_name", "county_name", "fips"
    "street", "city", "address_state", "zip_code",
    "po_street", "po_city", "po_state", "po_zip_code",
    "reg_authority_name", "reg_first", "reg_last",
    "reg_street", "reg_city", "reg_state", "reg_zip_code",
    "reg_po_street", "reg_po_city", "reg_po_state", "reg_po_zip_code",
    "reg_phone", "reg_fax", "reg_email", "reg_website", "reg_hours",
    "phone", "fax", "email", "website", "hours", "voter_state", "source", "review")]

#The following section grabs the spreadsheet and writes it to a file. (Writing it to a file isn't strictly necessary, but saves some time down the line.)

url = "http://election.dos.state.fl.us/SOE/FloridaSOE.xls"
filename = cdir + "florida-clerks.xls"

urllib.urlretrieve(url, filename)

#The desired data is on sheet 0 of the downloaded file.

data = xlrd.open_workbook(filename).sheet_by_index(0)

#Each county exists in a separate row in the source data, so this cycles through the data row by row.

for row in range(1, data.nrows):

	authority_name, first_name, last_name, county_name, town_name, fips, street, city, address_state, zip_code, po_street, po_city, po_state, po_zip_code, reg_authority_name, reg_first, reg_last, reg_street, reg_city, reg_state, reg_zip_code, reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code, reg_phone, reg_fax, reg_email, reg_website, reg_hours, phone, fax, email, website, hours, review = dogcatcher.begin(voter_state)

	#The authority name is consistent from county to county and not included in the data.

	authority_name = "Supervisor of Elections"

	
	first_name = " ".join(data.cell(row,2).value.split())
	last_name = " ".join(data.cell(row,4).value.split())

	county_name = " ".join(data.cell(row,0).value.split())

	street = " ".join(data.cell(row,9).value.split())
	po_street = " ".join(data.cell(row,8).value.split())
	if street:
		city = " ".join(data.cell(row,10).value.split())
		address_state = " ".join(data.cell(row,11).value.split())
		zip_code = " ".join(data.cell(row,12).value.split())
		if po_street:
			po_city = " ".join(data.cell(row,10).value.split())
			po_state = " ".join(data.cell(row,11).value.split())

			#Occasionally, there's a separate mailing zip code. This checks that, and grabs it if so. Otherwise, it assigns the main zip code to be the mailing zip code.

			if data.cell(row,13).value:
				po_zip_code = " ".join(data.cell(row,13).value.split())
			else:
				po_zip_code = " ".join(data.cell(row,12).value.split())
	else:
		po_city = " ".join(data.cell(row,10).value.split())
		po_state = " ".join(data.cell(row,11).value.split())
		po_zip_code = " ".join(data.cell(row,12).value.split())


	phone = dogcatcher.clean_phone(" ".join(data.cell(row,5).value.split()))
	fax = dogcatcher.clean_phone(" ".join(data.cell(row,6).value.split()))

	email = " ".join(data.cell(row,7).value.lower().split())

	website = dogcatcher.clean_website(data.cell(row,14).value.rstrip().replace("//","+++++"))

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