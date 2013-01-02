import urllib
import re
import sys
import dogcatcher
import HTMLParser
import os

h = HTMLParser.HTMLParser()

cdir = os.path.dirname(os.path.abspath(__file__)) + "/"

#acquiring the FIPs lists that are necessary later
fips_data_re = re.compile(".+?MD.+?\n")
fips_data = dogcatcher.make_fips_data(fips_data_re)
fips_numbers = dogcatcher.make_fips_numbers(fips_data)
fips_names = dogcatcher.make_fips_names(fips_data)

#The following section grabs the website and writes it to a file. (Writing it to a file isn't strictly necessary, but saves some time down the line.)
file_path = cdir + "maryland-clerks.html"
url = "http://www.elections.state.md.us/about/county_boards.html"
data = urllib.urlopen(url).read()
output = open(file_path,"w")
output.write(data)
output.close()

voter_state = "MD"
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

county_data_re = re.compile("<p>.*?<strong>(.+?)href=[^>]+?>Directions", re.DOTALL)
county_data_item_re = re.compile(".+?<br \>",re.DOTALL)
links_re = re.compile("(<a href=.+?>.+?</a>)")

email_re = re.compile(">([^<]+?@[^<]+?)<")
website_re = re.compile("href=\"(http[^@]+?)\"")

phone_re = re.compile("(\d{3}-\d{3}-\d{4}[^x]*?)<br />")
fax_re = re.compile("(\d{3}-\d{3}-\d{4}) \([Ff]ax")
phone_2_re = re.compile("\d{3}-\d{3}-\d{4}")

official_name_re = re.compile(".+<br />(.+?,.*? Director)", re.DOTALL)
middle_re = re.compile("[A-Z]\.* ")

county_name_re = re.compile("\s*(.+?)</strong><br />")

#address_re = re.compile("([^\n]*?\d.+?\d{5}[-\d]*?)<br />", re.DOTALL)
mailing_address_re = re.compile("Mailing Address: (.+?\d{5}[-\d]*?)<br />", re.DOTALL)
street_address_re = re.compile("Street Address: (.+?\d{5}[-\d]*?)<br />", re.DOTALL)
address_re = re.compile("</strong><br />(.+?\d{5}[-\d]*?)<br />", re.DOTALL)

csz_re = re.compile("[\n>,-] *([^,\n<]+?,* [A-Z]*,* *\d{5}[\d-]*)")
city_re = re.compile("(.+?),* [A-Z]{2,2},* *\d{5}[\d-]*")
state_re = re.compile(" ([A-Z]{2,2}),* [\d{5}]")
zip_re = re.compile(" (\d{5}[\d-]*)")

#city_state_re = re.compile(" ([^,]+?) MD")

data = data.replace("Centreville 21617","Centreville, MD 21617")

county_data = county_data_re.findall(data)

for county in county_data:

	authority_name, first_name, last_name, county_name, town_name, fips, street, city, address_state, zip_code, po_street, po_city, po_state, po_zip_code, reg_authority_name, reg_first, reg_last, reg_street, reg_city, reg_state, reg_zip_code, reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code, reg_phone, reg_fax, reg_email, reg_website, reg_hours, phone, fax, email, website, hours, review = dogcatcher.begin(voter_state)

	county_name = county_name_re.findall(county)[0].replace(" County","")

	county_data_item = county_data_item_re.findall(county)

	links = links_re.findall(county)

	email = dogcatcher.find_emails(email_re, county)

	website = dogcatcher.website_find(website_re, county)

	phone = dogcatcher.phone_find(phone_re, county)

	fax = dogcatcher.phone_find(fax_re, county)

	#fixing an edge case in Baltimore City
	if county_name == "Baltimore City":
		if "for Absentee Ballots Only" and "410-727-1775" in county:
			reg_fax = fax
			fax = "410-727-1775"
		else:
			print "Baltimore City edge case changed."
			sys.exit()


	print "_______________________________________"
	print county
	print "======================================="


	official_name = official_name_re.findall(county)[0].lstrip("\n ")
	first_name, last_name, authority_name, review = dogcatcher.make_name(official_name, ",", review)

	#This section generates the address. In Maryland, there's either a single street address, or explicitly delineated street and mailing addresses.
	#This checks whether the latter case is true. If so, it isolates both addresses and creates a street address, city, state, and zip separately.
	#If not, it creates only a street address.

	street_address_check = street_address_re.findall(county)

	if street_address_check:
		street_address = street_address_check[0]

		street_csz = csz_re.findall(street_address)[0]
		city = city_re.findall(street_csz)[0]
		address_state = state_re.findall(street_csz)[0]
		zip_code = zip_re.findall(street_csz)[0]
		street = street_address.replace(street_csz,"").replace("\r\n",", ").replace("<br />","").strip(", ")

		if county_name == "Montgomery" and "4333" in county and "20849-0369" in county: #Montgomery County is a mess; they use three separate PO boxes. 
			reg_po_street = "P.O. Box 4333"
			reg_po_city = "Rockville"
			reg_po_state = "MD"
			reg_po_zip_code = "20849-4333"

			po_street = "P.O. Box 10159"
			po_city = "Rockville"
			po_state = "MD"
			po_zip_code = "20849-0159"
		elif county_name == "Montgomery":
			print "Something's changed in Mongtgomery County."
			sys.exit()

		if not po_street:
			mailing_address = mailing_address_re.findall(county)[0]
			mailing_csz = csz_re.findall(mailing_address)[0]

			po_city = city_re.findall(mailing_csz)[0]
			po_state = state_re.findall(mailing_csz)[0]
			po_zip_code = zip_re.findall(mailing_csz)[0]
			po_street = mailing_address.replace(mailing_csz,"").replace("\r\n",", ").replace("<br />","").strip(", ")

	else:
		address = address_re.findall(county)[0]
		csz = csz_re.findall(address)[0]
		city = city_re.findall(csz)[0]
		address_state = state_re.findall(csz)[0]
		zip_code = zip_re.findall(csz)[0]
		street = address.replace(csz,"").replace("\r\n",", ").replace("<br />","").strip(", ")


	# street = street.replace("<br />",", ").replace("\n",", ").strip(",\n ").replace(" ,",",").replace(",,",",")
	# po_street = po_street.replace("<br />",", ").strip(",- ")


	
	if "FrederickCounty" in county:
		hours = "8:00 a.m to 4:30 p.m"
	else:
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

output = open(cdir + "maryland.txt", "w")
for r in result:
	r = h.unescape(r)
	output.write("\t".join(r))
	output.write("\n")
output.close()