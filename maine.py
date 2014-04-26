import mechanize
import re
import json
import time
import urllib
import dogcatcher
import HTMLParser
import os
import sys

h = HTMLParser.HTMLParser()

cdir = os.path.dirname(os.path.abspath(__file__)) + "/"

file_path = cdir + "maine-clerks.html"

url = "http://www.maine.gov/sos/cec/elec/munic.shtml"
data = urllib.urlopen(url).read()
output = open(file_path, "w")
output.write(data)
output.close()

result = [("authority_name", "first_name", "last_name", "town_name", "county_name", "fips",
    "street", "city", "address_state", "zip_code",
    "po_street", "po_city", "po_state", "po_zip_code",
    "reg_authority_name", "reg_first", "reg_last",
    "reg_street", "reg_city", "reg_state", "reg_zip_code",
    "reg_po_street", "reg_po_city", "reg_po_state", "reg_po_zip_code",
    "reg_phone", "reg_fax", "reg_email", "reg_website", "reg_hours",
    "phone", "fax", "email", "website", "hours", "voter_state", "source", "review")]

source = "State"
voter_state = "ME"

county_re = re.compile("<h2.+?>(.+?)</div><div style=\"clear:left;\">", re.DOTALL)
absentee_re = re.compile("Municipal Clerk(.+?)</dl>", re.DOTALL)
registrar_re = re.compile("Municipal Registrar(.+?)</dl>", re.DOTALL)

name_re = re.compile("<dd>.+?<p>(.+?)</p>", re.DOTALL)

csz_re = re.compile("(<p>[^\d]+?, *[A-Z][A-Z] *\d{5}[\d-]*</p>)")
city_re = re.compile("<p>(.+?),")
state_re = re.compile(" [A-Z][A-Z] ")
zip_re = re.compile("\d{5}[-\d]*")
address_re = re.compile("</p>.+?<p>(.+? \d{5}[\d-]*</p>)", re.DOTALL)
po_re = re.compile("(P.* *O.* .+?)</p>")

phone_re = re.compile("Phone: (.+?)")
fax_re = re.compile("Fax: (.+?)")

town_name_re = re.compile("(.+?)</h2>")

data = open(file_path).read()
data = data.replace("<p style=\"clear:both;\">Last Updated:","</div><div style=\"clear:left;\">")
data = dogcatcher.po_standardize(data)

county_data = county_re.findall(data)

for county in county_data:

	authority_name, first_name, last_name, county_name, town_name, fips, street, city, address_state, zip_code, po_street, po_city, po_state, po_zip_code, reg_authority_name, reg_first, reg_last, reg_street, reg_city, reg_state, reg_zip_code, reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code, reg_phone, reg_fax, reg_email, reg_website, reg_hours, phone, fax, email, website, hours, review = dogcatcher.begin(voter_state)

	authority_name = "Municipal Clerk"
	print authority_name

	#There are many edits to town names needed to make the data come off of the Google Maps API well.
	town_name = town_name_re.findall(county)[0].replace("Plt","Plantation").strip(".")

	if town_name == "Rockwood Strip":
		town_name = town_name.replace(" Strip","")
	if town_name == "Dennistown Plantation" or "Oxbow P" in town_name:
		town_name = town_name.replace(" Plantation","")
	if "Pleasant Point" in town_name:
		town_name = town_name.replace(" Voting District","")

	#This separates the person who handles registrations and the person who handles absentee ballot requests.
	absentee = absentee_re.findall(county)[0]
	registrar = registrar_re.findall(county)[0]

	official_name = name_re.findall(absentee)[0].strip()
	first_name, last_name, review = dogcatcher.split_name(official_name, review)

	phone = dogcatcher.find_phone(phone_re, absentee)

	fax = dogcatcher.find_phone(fax_re, absentee)

	#This section finds athe address. After finding the address, it identifies a city/state/zip (csz) combination and a PO Box number if that exists.
    #It removes both the CSZ and the PO Address (if it exists) from the full address, leaving behind a street address with some garbage.
    #It then cleans up the street address and pulls the city, state, and zip out of the csz, and assigns them as appropriate to the street address and mailing address.

	address = address_re.findall(absentee)[0]

	csz = csz_re.findall(address)[0].strip()

	try:
		po_street = po_re.findall(address)[0]
	except:
		po_street = ""

	street = ", ".join(address.replace(csz,"").replace(po_street,"").replace("<p>","").split("</p>")).replace("\r\n","").strip(", ")

	if street:
		csz = csz_re.findall(address)[0].strip()
		city = city_re.findall(csz)[0].strip()
		address_state = state_re.findall(csz)[0].strip()
		zip_code = zip_re.findall(csz)[0].strip()
	if po_street:
		po_city = city_re.findall(csz)[0].strip()
		po_state = state_re.findall(csz)[0].strip()
		po_zip_code = zip_re.findall(csz)[0].strip()


	#The Google API doesn't take the word "Twp" well in several towns. (And in townships, it's common for the clerk's address to be outside of the Twp.) This cleans it out.
	#However, it fails if "No 21 Twp" is give as No 21, instead of No 21 Twp, so for that one we don't replace it.
	if city and "No 21" not in town_name:
		if town_name != city:
			town_name = town_name.replace(" Twp","").replace("Strip","")
	elif po_city and "No 21" not in town_name:
		if town_name != po_city:
			town_name = town_name.replace(" Twp","")

	print "__________________________________________________________"


	#There are many towns where the reg person is the same as the absentee person; this is denoted by the words "Same as." We check for that.


	if "Same as" not in registrar:

		official_name = name_re.findall(registrar)[0].strip()
		reg_first, reg_last, review = dogcatcher.split_name(official_name, review)

		reg_phone = dogcatcher.find_phone(phone_re, registrar)

		reg_fax = dogcatcher.find_phone(fax_re, registrar)

		# This section finds the registration official's address. After finding the address, it identifies a city/state/zip (csz) combination and a PO Box number if that exists.
		#It removes both the CSZ and the PO Address (if it exists) from the full address, leaving behind a street address with some garbage.
		#It then cleans up the street address and pulls the city, state, and zip out of the csz, and assigns them as appropriate to the street address and mailing address.

		reg_address = address_re.findall(registrar)[0]
		reg_csz = csz_re.findall(reg_address)[0].strip()

		try:
			reg_po_street = po_re.findall(reg_address)[0]
		except:
			reg_po_street = ""

		reg_street = ", ".join(reg_address.replace(reg_csz,"").replace(reg_po_street,"").replace("<p>","").split("</p>")).strip("\r\n, ")

		if reg_street:
			reg_city = city_re.findall(reg_csz)[0].strip()
			reg_state = state_re.findall(reg_csz)[0].strip()
			reg_zip_code = zip_re.findall(reg_csz)[0].strip()
		if reg_po_street:
			reg_po_city = city_re.findall(reg_csz)[0].strip()
			reg_po_state = state_re.findall(reg_csz)[0].strip()
			reg_po_zip_code = zip_re.findall(reg_csz)[0].strip()

		reg_authority_name = "Municipal Registrar"

	print town_name

	try:

		if street:
			fips, county_name = dogcatcher.map_fips(town_name, "ME", zip_code, city)
		else:
			fips, county_name = dogcatcher.map_fips(town_name, "ME", po_zip_code, po_city)

	except: #Several towns don't work correctly in the Google Maps API.

		if town_name == "Magalloway Plantation" or town_name == "Lincoln Plantation":
			county_name = "Oxford"

		elif town_name == "Winterville Plantation":
			county_name = "Aroostook"

		else:
			print "There's a new broken town: " + town_name
			if street:
				print town_name + " ME " + zip_code
			else:
				print town_name + " ME " + po_zip_code
			sys.exit()

		fips = dogcatcher.find_fips(county_name, voter_state)


	result.append([authority_name, first_name, last_name, town_name, county_name, fips,
	street, city, address_state, zip_code,
	po_street, po_city, po_state, po_zip_code,
	reg_authority_name, reg_first, reg_last,
	reg_street, reg_city, reg_state, reg_zip_code,
	reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code,
	reg_phone, reg_fax, reg_email, reg_website, reg_hours,
	phone, fax, email, website, hours, voter_state, source, review])


#This outputs the results to a separate text file. Since Maine uses cities, it outputs to a file in the cities folder.

dogcatcher.output(result, voter_state, cdir, "cities")