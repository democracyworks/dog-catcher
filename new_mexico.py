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
fips_data_re = re.compile(".+?NM.+?\n")
fips_data = dogcatcher.make_fips_data(fips_data_re)
fips_numbers = dogcatcher.make_fips_numbers(fips_data)
fips_names = dogcatcher.make_fips_names(fips_data)

#The following section grabs the website and writes it to a file. (Writing it to a file isn't strictly necessary, but saves some time down the line.)

file_path = cdir + "new-mexico-clerks.html"

url = "http://www.sos.state.nm.us/Voter_Information/County_Clerk_Information.aspx"
data = urllib.urlopen(url).read()
output = open(file_path,"w")
output.write(data)
output.close()
voter_state = "NM"
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

county_data_re = re.compile("(<H2>.+?</P>)", re.DOTALL)
county_name_re = re.compile("<H2>(.+?)</H2>")
county_data_item_re = re.compile("(.+?)<BR>")
zip_re = re.compile("\d{5}-\d{4}|\d{5}")
end_re =re.compile(".+?, *[A-Z][A-Z] *\d{5}[\d-]*")
email_re = re.compile("Email: <A href=\".+?\">(.+?)</A>")
phone_re = re.compile("Phone: (.+?)<BR>")
fax_re = re.compile("Fax: (.+?)<BR>")
middle_name_re = re.compile(" ([a-zA-z]\. )")
po_re = re.compile("[P\.O ]*Box \d+")
state_re = re.compile(" [A-Z][A-Z]")
city_re = re.compile("(.+?),")

address_re = re.compile("\)<BR>(.+, [A-Z]{2,2} +\d{5}[\d-]*)<", re.DOTALL)
csz_re = re.compile("[A-Za-z ]+, [A-Z]{2,2} +\d{5}[\d-]*")

dona_ana_re = re.compile("Do.+a Ana")

	
data = data.replace("&nbsp;"," ")
data = data.replace("P.O. Box 767Estancia","P.O. Box 767<BR>Estancia")#second replace fixes a bug in Estancia, NM

for item in dona_ana_re.findall(data): #There's an accent mark in Dona Ana that Sublime can't really handle.
	print item
	data = data.replace(item, "Dona Ana")

county_data = county_data_re.findall(data)

for county in county_data:
	
	authority_name, first_name, last_name, county_name, town_name, fips, street, city, address_state, zip_code, po_street, po_city, po_state, po_zip_code, reg_authority_name, reg_first, reg_last, reg_street, reg_city, reg_state, reg_zip_code, reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code, reg_phone, reg_fax, reg_email, reg_website, reg_hours, phone, fax, email, website, hours, review = dogcatcher.begin(voter_state)

	county_name = county_name_re.findall(county)[0]

	county_data_item = county_data_item_re.findall(county)

	authority_name = "Clerk"

	official_name = county_data_item[0].replace("<P>Clerk: ","").replace("(D)","").replace("(R)","").strip()
	first_name, last_name, review = dogcatcher.split_name(official_name, review)

	#This section finds the address. After finding the address, it identifies a city/state/zip (csz) combination and a PO Box number if that exists.
    #It removes both the CSZ and the PO Address (if it exists) from the full address, leaving behind a street address with some garbage.
    #It then cleans up the street address and pulls the city, state, and zip out of the csz, and assigns them as appropriate to the street address and state.

	address = address_re.findall(county)[0]

	print [address]

	csz = csz_re.findall(address)[0]

	try:
		po_street = po_re.findall(address)[0].replace(csz,"").strip(", \n").replace("<BR>",", ")
	except:
		po_street = ""

	street = address.replace(po_street,"").replace(csz,"").replace("<BR>",", ")
	street = street.replace("\n",", ").replace("\r","").replace(" ,",",").strip(" \n/,")

	if po_street:
		if street:
			city = city_re.findall(csz)[0]
			address_state = state_re.findall(csz)[0]
			zip_code = zip_re.findall(csz)[0]
		po_city = city_re.findall(csz)[0].strip()
		po_state = state_re.findall(csz)[0].strip()
		po_zip_code = zip_re.findall(csz)[0].strip()
	else:
		city = city_re.findall(csz)[0].strip()
		address_state = state_re.findall(csz)[0].strip()
		zip_code = zip_re.findall(csz)[0].strip()


	street = " ".join(street.strip(",- ").split())
	po_street = " ".join(po_street.strip(",- ").split())		

	email = dogcatcher.find_emails(email_re, county)

	phone = dogcatcher.phone_find(phone_re, county)

	fax = dogcatcher.phone_find(fax_re, county)

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

output = open(cdir + "new_mexico.txt", "w")
for r in result:
	r = h.unescape(r)
	output.write("\t".join(r))
	output.write("\n")
output.close()