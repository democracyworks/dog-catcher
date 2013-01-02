import urllib
import re
import sys
import json
import time
import dogcatcher

#acquiring the FIPs lists that are necessary later
fips_data_re = re.compile(".+?CA.+?\n")
fips_data = dogcatcher.make_fips_data(fips_data_re)
fips_numbers = dogcatcher.make_fips_numbers(fips_data)
fips_names = dogcatcher.make_fips_names(fips_data)

voter_state = "NH"
source = "State"

#Currently I grab the CSV file by hand. At some point, I will need to grab it using mechanize.

file_path = "C:\Users\pkoms\Documents\TurboVote\Scraping\\new_hampshire-clerks.csv"

result = [("authority_name", "first_name", "last_name", "town_name", "county_name", "fips",
	"street", "city", "address_state", "zip_code",
	"po_street", "po_city", "po_state", "po_zip_code",
	"reg_authority_name", "reg_first", "reg_last",
	"reg_street", "reg_city", "reg_state", "reg_zip_code",
	"reg_po_street", "reg_po_city", "reg_po_state", "reg_po_zip_code",
	"reg_phone", "reg_fax", "reg_email", "reg_website", "reg_hours",
	"phone", "fax", "email", "website", "hours", "voter_state", "source", "review")]

data = open(file_path).read()

town_data_re = re.compile("[A-Z][A-Z].+?\n", re.DOTALL)
town_item_re = re.compile("(.+?),")

middle_name_re = re.compile(" ([a-zA-z]\.* )")
po_re = re.compile("P *O BOX \d+")
po_2_re = re.compile("\d+ P *O BOX")
po_city_re = re.compile("[A-Za-z \.]+? \d{5}[\d-]*")
zip_re = re.compile("\d{5}[\d-]*")

#When there isn't a mailing address, we have to be able to distinguish the street address from the city name. So, through trial, error, and guesswork, it checks this entire list.

street_1_re = re.compile(".+? [DR][DR]\.* ")
street_2_re = re.compile(".+? ROAD ")
street_3_re = re.compile(".+? S[QT]\.* ")
street_4_re = re.compile(".+? STREET ")
street_5_re = re.compile(".+? RO*U*TE*  *\d+[A-Z]* ")
street_6_re = re.compile(".+? AVEN*U*E* ")
street_7_re = re.compile(".+? HI*G*H*WA*Y ")
street_8_re = re.compile(".+? WAY ")
street_9_re = re.compile(".+? PLAZA ")
street_10_re = re.compile(".+? SQUARE ")
street_11_re = re.compile(".+? TPKE ")
street_12_re = re.compile(".+? VILLAGE GREEN ")
street_24_re = re.compile(".+? MAIN ")
street_25_re = re.compile(".+? WASHINGTON ")


town_data = town_data_re.findall(data)


for town in town_data:
	
	authority_name, first_name, last_name, county_name, town_name, fips, street, city, address_state, zip_code, po_street, po_city, po_state, po_zip_code, reg_authority_name, reg_first, reg_last, reg_street, reg_city, reg_state, reg_zip_code, reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code, reg_phone, reg_fax, reg_email, reg_website, reg_hours, phone, fax, email, website, hours, review = dogcatcher.begin(voter_state)	

	town = town.replace(",,",", ,").replace("'S","'s")

	#Since the data is in a CSV format, we can easily split into items. This is helpful, since usually each item is a distinct type of data.
 	town_item = town_item_re.findall(town) 
 	
	town_name = town_item[0].title().replace("Ward","").strip(" 0123456789").replace("'S","'s")

	official_name = town_item[1].title()

	first_name, last_name, review = dogcatcher.name(official_name, middle_name_re, review)


	phone = "(603)" + town_item[3]

	if town_item[4] != " ":
		fax = "(603)" + town_item[4]
	else:
		fax = ""
	if fax == "(603)155-9128":
		fax = "(603)755-9128"

	email = town_item[5].lower()

	if website == "none available" or website == " ":
		website = ""
	else:
		website = dogcatcher.website_clean(town_item[6])

	#The full address is its own item, and there's either a PO Box or nothing. This block of code:
	#1. Checks for a PO Box. If so, extracts it. It then checks for a city and zip code the same way. If there's no zip code, it grabs it form the polling place indicated in later column.
	#2. If no PO Box, it extracts a street address (details described earlier), and then a zip code and city.

	address = town_item[2]
	if "O BOX" in address:
		try: 
			po_street = po_re.findall(address)[0].strip()
		except:
			po_street = po_2_re.findall(address)[0].strip()
		try:
			po_city = po_city_re.findall(address)[0].strip()
		except:
			po_city = town_name
		try:
			po_zip = zip_re.findall(address)[0]
		except:
			po_zip = zip_re.findall(town_item[7])[0]

	else:
		if street_1_re.findall(address):
			street = street_1_re.findall(address)[0]
		elif street_2_re.findall(address):
			street = street_2_re.findall(address)[0]
		elif street_3_re.findall(address):
			street = street_3_re.findall(address)[0]
		elif street_4_re.findall(address):
			street = street_4_re.findall(address)[0]
		elif street_5_re.findall(address):
			street = street_5_re.findall(address)[0]
		elif street_6_re.findall(address):
			street = street_6_re.findall(address)[0]
		elif street_7_re.findall(address):
			street = street_7_re.findall(address)[0]
		elif street_8_re.findall(address):
			street = street_8_re.findall(address)[0]
		elif street_9_re.findall(address):
			street = street_9_re.findall(address)[0]
		elif street_10_re.findall(address):
			street = street_10_re.findall(address)[0]
		elif street_11_re.findall(address):
			street = street_11_re.findall(address)[0]
		elif street_12_re.findall(address):
			street = street_12_re.findall(address)[0]
		elif street_24_re.findall(address):
			street = street_24_re.findall(address)[0]
		elif street_25_re.findall(address):
			street = street_25_re.findall(address)[0]
		zip_code = zip_re.findall(address)[0]
		city = address.replace(street,"").replace(zip_code,"").strip()


	if street:
		fips, county_name = dogcatcher.maps_fips(city, address_state, zip_code, fips_names, fips_numbers)
	else:
		fips, county_name = dogcatcher.maps_fips(po_city, po_state, po_zip_code, fips_names, fips_numbers)

	#Both of these towns aren't found well in Google's data.

	if town_name == "Pinkham's Grant":
		county_name = "Coos"
		fips = dogcatcher.fips_find(county_name, fips_names, fips_numbers)

	if town_name == "Sargent's Purchase":
		county_name = "Coos"
		fips = dogcatcher.fips_find(county_name, fips_names, fips_numbers)

	#The authority name is consistent from county to county and not included in the data.

	authority_name = "Clerk"

	result.append([authority_name, first_name, last_name, town_name, county_name, fips,
	street, city, address_state, zip_code,
	po_street, po_city, po_state, po_zip_code,
	reg_authority_name, reg_first, reg_last,
	reg_street, reg_city, reg_state, reg_zip_code,
	reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code,
	reg_phone, reg_fax, reg_email, reg_website, reg_hours,
	phone, fax, email, website, hours, voter_state, source, review])

#In several larger towns, there are multiple entries. (One entry per ward.) These become identical in the data. This function checks for these and wipes them out as appropriate.

for item in result:
	end = len(result)
	x = 0
	for i in range(result.index(item)+1,len(result)):
		if item == result[i-x]:
			print result[i-x]
			result.pop(i-x)
			x = x + 1

output = open("C:\Users\pkoms\Documents\TurboVote\Scraping\\new_hampshire.txt", "w")
for r in result:
	output.write("\t".join(r))
	output.write("\n")
output.close()