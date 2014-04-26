import urllib
import re
import sys
import dogcatcher
import HTMLParser
import os

h = HTMLParser.HTMLParser()

cdir = os.path.dirname(os.path.abspath(__file__)) + "/"

#The following section grabs the website and writes it to a file. (Writing it to a file isn't strictly necessary, but saves some time down the line.)

file_path = cdir + "iowa-counties.html"
url = "http://sos.iowa.gov/elections/auditors/auditor.asp?CountyID=00"
data = urllib.urlopen(url).read()
output = open(file_path,"w")
output.write(data)
output.close()

voter_state = "IA"
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

county_data_re = re.compile("<h2>[^<>]+?\(.\).+?</table>", re.DOTALL)
county_name_re = re.compile(">(.+?) -")

email_re = re.compile("mailto:(.+?)\"")
website_re = re.compile("Website[^\s]+?\s+[^\s]+?<td colspan=\"2\"><a href=\"(http://.+?)\">.+?</a></td></tr>", re.DOTALL)
hours_re = re.compile("Hours.+?colspan=\"2\">(.+?)<",re.DOTALL)
phone_re = re.compile("\">(\d{3}-\d{3}-\d{4})<")
fax_re = re.compile("d>(\d{3}-\d{3}-\d{4})<")

physical_re = re.compile("Physical Address.+?<td>\s+([^\s].+?)</td>", re.DOTALL)
mailing_re = re.compile("Mailing Address.+?<td.+?>\s+([^\s].+?)</td>", re.DOTALL)

official_name_re = re.compile("alt=\"(.+?),")

csz_re = re.compile("\s+(.+?[A-Z][A-Z]\d{5}[\d-]*)")

city_re = re.compile("(.+?)[A-Z][A-Z]")
state_re = re.compile("[A-Z][A-Z]")
zip_re = re.compile("\d{5}[\d-]*")

#The first change makes the data more approachable 

#data = data.replace("\r\n\t\t\t\t\t\t\t\t","\r\n")
data = data.replace("&nbsp;","")



county_data = county_data_re.findall(data)

for county in county_data:

	authority_name, first_name, last_name, county_name, town_name, fips, street, city, address_state, zip_code, po_street, po_city, po_state, po_zip_code, reg_authority_name, reg_first, reg_last, reg_street, reg_city, reg_state, reg_zip_code, reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code, reg_phone, reg_fax, reg_email, reg_website, reg_hours, phone, fax, email, website, hours, review = dogcatcher.begin(voter_state)

	authority_name = "County Auditor"

	# print "______________________________________________"
	# print county
	# print "++++++++++++++++++++++++++++++++++++++++++++++"

	official_name = official_name_re.findall(county)[0].partition(" ")
	first_name, last_name, review = dogcatcher.split_name(official_name, review)

	county_name = county_name_re.findall(county)[0]

	email = dogcatcher.find_emails(email_re, county)

	website = dogcatcher.find_website(website_re, county)

	hours = hours_re.findall(county)[0]

	phone = dogcatcher.find_phone(phone_re, county)

	fax = dogcatcher.find_phone(fax_re, county)

	#The street and mailing addresses are stored in two different places. They may be the same.
	#This grabs both; trims both, and removes the street address from the mailing address.
	#If the mailing adddress still exists, it turns both into a proper address.
	#If not, it just creates a street address.

	address = physical_re.findall(county)[0].replace("<br />","")
	mailing = mailing_re.findall(county)[0].replace("<br />","")

	address_csz = csz_re.findall(address)[0]
	mailing_csz = csz_re.findall(mailing)[0]

	street = address.replace(address_csz,"").strip("\r\n\t ")
	po_street = mailing.replace(mailing_csz,"").strip("\r\n\t ").replace(street)

	if po_street:
		city = city_re.findall(address_csz)[0].strip()
		address_state = state_re.findall(address_csz)[0].strip()
		zip_code = zip_re.findall(address_csz)[0].strip()
		po_city = city_re.findall(mailing_csz)[0].strip()
		po_state = state_re.findall(mailing_csz)[0].strip()
		po_zip_code = zip_re.findall(mailing_csz)[0].strip()
	else:		
		city = city_re.findall(address_csz)[0].strip()
		address_state = state_re.findall(address_csz)[0].strip()
		zip_code = zip_re.findall(address_csz)[0].strip()

	if "PO Box" not in po_street and po_street:
		review = review + "h"

	if po_street.find("PO Box") !=0 and po_street:
		review = review + "j"

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

output = open(cdir + "iowa.txt", "w")
for r in result:
    r = h.unescape(r)
    output.write("\t".join(r))
    output.write("\n")
output.close()