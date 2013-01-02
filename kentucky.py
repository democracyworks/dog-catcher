import urllib
import urllib2
import re
import sys
import dogcatcher
import HTMLParser
import os

h = HTMLParser.HTMLParser()

cdir = os.path.dirname(os.path.abspath(__file__)) + "/"

#acquiring the FIPs lists that are necessary later
fips_data_re = re.compile(".+?KY.+?\n")
fips_data = dogcatcher.make_fips_data(fips_data_re)
fips_numbers = dogcatcher.make_fips_numbers(fips_data)
fips_names = dogcatcher.make_fips_names(fips_data)

#The following section grabs the website and writes it to a file. (Writing it to a file isn't strictly necessary, but saves some time down the line.)


voter_state = "KY"
source = "State"

result = [("authority_name", "first_name", "last_name", "county_name", "fips",
    "street", "city", "address_state", "zip_code",
    "po_street", "po_city", "po_state", "po_zip_code",
    "reg_authority_name", "reg_first", "reg_last",
    "reg_street", "reg_city", "reg_state", "reg_zip_code",
    "reg_po_street", "reg_po_city", "reg_po_state", "reg_po_zip_code",
    "reg_phone", "reg_fax", "reg_email", "reg_website", "reg_hours",
    "phone", "fax", "email", "website", "hours", "voter_state", "source", "review")]

#The Kentucky SoS website stores county clerk info in a series of pages broken down by first letter of county.
#Some pages aggregate two or more letters.
#This grabs each page; adds it to a long string; and eventually writes that string to a file as the Kentucky County Clerks data.
#(Writing it to a file isn't strictly necessary, but saves some time down the line.)

alphabet = ["A", "B", "C", "D-F", "G", "H", "I-J", "K",
			"L", "M", "N-O", "P-Q", "R", "S", "T-V", "W-Z"]


user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
headers = {'User-Agent' : user_agent}

county_data = ""

for letter in alphabet:

	county_url = "http://elect.ky.gov/contactcountyclerks/Pages/" + letter + ".aspx"
	req = urllib2.Request(county_url, headers=headers)
	print county_url
	try:
		data = urllib2.urlopen(req).read()
	except:
		print "The URLs must have changed."
		break
	marker = "!!!!!!!!!" + letter + letter + letter + letter + "!!!!!!!!!" #makes sure the file divisions are clear
	county_data = county_data + "\n" + marker + data

file_path = cdir + "kentucky-clerks.html"
output = open(file_path,"w")
output.write(county_data)
output.close()

data = open(file_path).read()

county_data_re = re.compile("<h3>.+? County Clerk.+?</p>", re.DOTALL)
county_name_re = re.compile("<h3>(.+?)</h3>")

email_re = re.compile("mailto:(.+?)\"")
website_re = re.compile("href=\"(http.+?)\"")

official_name_re = re.compile("<p>(.+?)<br>")

phone_re = re.compile("Phone: (.+?)<br>")
fax_re = re.compile("F[Aa][Xx]: (.+?)<br>")

strange_character_kill_re = re.compile("Website:(.+?)<a href=\"http://www.triggcountyclerk.ky.gov\">")

for strange in strange_character_kill_re.findall(data):
	data = data.replace(strange,"")


address_re = re.compile("<p>[^<>]*?<br>(.+?)Phone", re.DOTALL)

csz_re = re.compile(" *(<br>[^,<>]+?,* [A-Z][A-Z] *\d{5}[\d-]*)")
city_re = re.compile("([^<>]+?),* [A-Z][A-Z]")
state_re = re.compile(" ([A-Z][A-Z]) ")
zip_re = re.compile(" (\d{5}[\d-]*)")
po_re = re.compile("(P\.* *O\.* Box .+?)<br>", re.DOTALL)

hours_re =re.compile("<br>([^<>]+?)</p>")

county_data = county_data_re.findall(data)

for county in county_data:

	authority_name, first_name, last_name, county_name, town_name, fips, street, city, address_state, zip_code, po_street, po_city, po_state, po_zip_code, reg_authority_name, reg_first, reg_last, reg_street, reg_city, reg_state, reg_zip_code, reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code, reg_phone, reg_fax, reg_email, reg_website, reg_hours, phone, fax, email, website, hours, review = dogcatcher.begin(voter_state)

	authority_name = "Clerk"

	if "<h3>Jefferson County Clerk</h3>" in county:
		continue
	county_name = county_name_re.findall(county)[0].replace("County Clerk","").replace("Election Center","").replace("<br>","").strip()

	official_name = official_name_re.findall(county)[0].lstrip("\n ")
	first_name, last_name, review = dogcatcher.split_name(official_name, review)

	email = dogcatcher.find_emails(email_re, county)

	website = dogcatcher.website_find(website_re, county)

	phone = dogcatcher.phone_find(phone_re, county)

	fax = dogcatcher.phone_find(fax_re, county)

	#This section finds the address. After finding the address, it identifies a city/state/zip (csz) combination and a PO Box number if that exists.
	#It removes both the CSZ and the PO Address (if it exists) from the full address, leaving behind a street address with some garbage.
	#It then cleans up the street address and pulls the city, state, and zip out of the csz, and assigns them as appropriate to the street address and state.

	address = address_re.findall(county)[0]

	csz = csz_re.findall(address)[0]

	try:
		po_street = po_re.findall(address)[0].strip(", \n")
	except:
		po_street = ""

	street = address.replace(po_street,"").replace(csz,"").replace("<br>",", ")
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

	#There is some additional clarifying text in both the street and mailing address in some cases; this cleans it out.

	street = street.replace(" (location)","").replace("Location: ","")
	po_street = po_street.replace(" (mailing address)","").replace("Mail: ","").replace(" (all correspondence)","")

	try:
		hours = hours_re.findall(county)[0]
	except:
		hours = ""

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

output = open(cdir + "kentucky.txt", "w")
for r in result:
	r = h.unescape(r)
    output.write("\t".join(r))
    output.write("\n")
output.close()