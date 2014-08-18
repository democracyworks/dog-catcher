import urllib
import re
import sys
import dogcatcher
import HTMLParser
import os

h = HTMLParser.HTMLParser()

cdir = os.path.dirname(os.path.abspath(__file__)) + "/"
tmpdir = cdir + "tmp/"

voter_state = "MS"
source = "State"

#The following section grabs the website and writes it to a file. (Writing it to a file isn't strictly necessary, but saves some time down the line.)
file_path = tmpdir + "mississippi-clerks.html"
url = "http://www.sos.ms.gov/elections_voter_info_center_absentee.aspx"
data = urllib.urlopen(url).read()
output = open(file_path,"w")
output.write(data)
output.close()

data = open(file_path).read()

result = [("authority_name", "first_name", "last_name", "county_name", "fips",
    "street", "city", "address_state", "zip_code",
    "po_street", "po_city", "po_state", "po_zip_code",
    "reg_authority_name", "reg_first", "reg_last",
    "reg_street", "reg_city", "reg_state", "reg_zip_code",
    "reg_po_street", "reg_po_city", "reg_po_state", "reg_po_zip_code",
    "reg_phone", "reg_fax", "reg_email", "reg_website", "reg_hours",
    "phone", "fax", "email", "website", "hours", "voter_state", "source", "review")]

county_data_re = re.compile("<tr>[^<]+?<td>[^<].+?\d.+?</td>[^<]+?</tr>", re.DOTALL)
county_name_re = re.compile("<td> *([A-Z \n\r]+) *</td>")

phone_fax_re = re.compile("\d{3}-\d{3}-.+?<.+?\d{4}", re.DOTALL)
number_re = re.compile("\d{3}-\d{3}-\d{4}")

address_re = re.compile("<td>.+?<td>(.+?)</td>[\s]+<td>\d{3}-\d{3}", re.DOTALL)
csz_re = re.compile("<br />[\s]*([^<]+? \d{5}[\d-]*)", re.DOTALL)
city_re = re.compile("([^\d]+?) \d{5}")
zip_re = re.compile(" (\d{5}[\d-]*)")

county_data = county_data_re.findall(data)

for county in county_data:
	print "__________________________________________________"

	authority_name, first_name, last_name, county_name, town_name, fips, street, city, address_state, zip_code, po_street, po_city, po_state, po_zip_code, reg_authority_name, reg_first, reg_last, reg_street, reg_city, reg_state, reg_zip_code, reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code, reg_phone, reg_fax, reg_email, reg_website, reg_hours, phone, fax, email, website, hours, review = dogcatcher.begin(voter_state)

	authority_name = "County Voter Registrar"

	print county

	county_name = " ".join(county_name_re.findall(county)[0].replace("\r\n"," ").title().split())

	#There is only one address in any town, which is either a PO box or physical address.
	#This grabs the address, determines which it is by checking for the words "P.O. Box", and acts accordingly.

	address = address_re.findall(county)[0]

	csz = csz_re.findall(address)[0]

	if "P.O. Box" in address:
		po_city = city_re.findall(csz)[0]
		po_zip_code = zip_re.findall(csz)[0]
		po_street = address.replace(csz,"").replace("\n\r",", ").replace("<br />","").strip(" \n\r,")
	else:
		city = city_re.findall(csz)[0]
		zip_code = zip_re.findall(csz)[0]
		street = " ".join(address.replace(csz,"").split()).replace("<br />","").strip(" \n\r,")

	print "++++++++++++++++++++++++++++++++++++++++++++"

	print [address]

	print [po_street + street]

	phone_fax = phone_fax_re.findall(county)[0]

	phone = dogcatcher.clean_phone(number_re.findall(phone_fax)[0])
	fax = dogcatcher.clean_phone(number_re.findall(phone_fax)[1])


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
