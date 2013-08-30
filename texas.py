import re
import sys
import urllib
import dogcatcher
import HTMLParser
import os
import json
import time
import csv

h = HTMLParser.HTMLParser()

cdir = os.path.dirname(os.path.abspath(__file__)) + "/"

#The following section grabs the website and writes it to a file. (Writing it to a file isn't strictly necessary, but saves some time down the line.)

voter_state = "TX"
source = "State"


result = [("authority_name", "first_name", "last_name", "county_name", "fips",
	"street", "city", "address_state", "zip_code",
	"po_street", "po_city", "po_state", "po_zip_code",
	"reg_authority_name", "reg_first", "reg_last",
	"reg_street", "reg_city", "reg_state", "reg_zip_code",
	"reg_po_street", "reg_po_city", "reg_po_state", "reg_po_zip_code",
	"reg_phone", "reg_fax", "reg_email", "reg_website", "reg_hours",
	"phone", "fax", "email", "website", "hours", "voter_state", "source", "review")]

file_path = cdir + "texas-clerks.html"
reg_file_path = cdir + "texas-reg-clerks.html"

# url = "http://www.sos.state.tx.us/elections/voter/county.shtml"
# data = urllib.urlopen(url).read()
# output = open(file_path,"w")
# output.write(data)
# output.close()

# reg_url = "http://www.sos.state.tx.us/elections/voter/votregduties.shtml"
# reg_data = urllib.urlopen(reg_url).read()
# output = open(reg_file_path,"w")
# output.write(reg_data)
# output.close()

data = open(file_path).read()
reg_data = open(reg_file_path).read()

data = dogcatcher.po_standardize(data.replace("&quot;","'").replace("&amp;","&").replace(", TX",""))
reg_data = dogcatcher.po_standardize(reg_data.replace("&quot;","'").replace(", TX",""))

no_space_re = re.compile(",[^\s]")

for item in no_space_re.findall(data):
	data = data.replace(item, dogcatcher.insert(item, " ", 1))

for item in no_space_re.findall(reg_data):
	data = data.replace(item, dogcatcher.insert(item, " ", 1))


county_re = re.compile("<dl>\s*(<dt>.+?</dd>)\s*</dl>", re.DOTALL)
county_data_item_re = re.compile("dd>([^\n\r]+?\s*[^\n<]*?)\s*<",re.DOTALL)
reg_county_data_item_re = re.compile("dd>(.+?)\s*<", re.DOTALL)
county_name_re = re.compile("<..>([^<>]+?)</dt>")

name_re = re.compile("[^\d]+?")
middle_name_re = re.compile(" ([a-zA-z]\. )")

phone_re = re.compile(">(\(\d{3}\) \d{3}-\d{4}.*?)<")
reg_phone_re = re.compile(">(\(\d{3}\) \d{3}-\d{4}[/ext\.\d ]*).*?<", re.DOTALL)
fax_re = re.compile("FAX: (\(\d{3}\) \d{3}-\d{4})")
reg_fax_re = re.compile("(\(\d{3}\) \d{3}-\d{4}[^>]*?)\n* FAX", re.DOTALL)

suite_re = re.compile("Ste[. ]+[\dA-Z]+")
zip_re = re.compile("(?<!\d)\d{5}(?!\d)[-\d]*")

city_1_re = re.compile("\d ([^,\d]+?) \d{5}[-\d]*") #If the street address ends in a digit and the city is one word, it's very easy to tell where the street address ends.
city_2_re = re.compile(" ([A-Za-z]) [^,\d]+? \d{5}[-\d]*") 
city_3_re = re.compile(", ([^,\d]+?) \d{5}[-\d]*")  #Here, we take the last comma (if there's one with no digits after it) and get everything after it.
city_4_re = re.compile(" ([^,\d]+?) \d{5}[-\d]*") #Here, we just take the last several words without commas or digits. This is not a promising regex.

po_re = re.compile("PO ")
po_letter_re = re.compile("([PO ]*[BD][oawer]+?[xr]  *[A-Z])") #For the handful of places with "PO Box [A-Z]" in their address.
po_street_re = re.compile("[PO ]*[BD][oawer]+?[xr] *\d+")
street_address_re = re.compile(">(.+?) P\.O\.")
street_re = re.compile("(.+),*")

digit_re = re.compile("\d")

#The part where the intern adds a bunch of code copied from other scrapers without knowing what it does.

county_data = county_re.findall(data)
reg_county_data = county_re.findall(reg_data)

for county in county_data:

	authority_name, first_name, last_name, county_name, town_name, fips, street, city, address_state, zip_code, po_street, po_city, po_state, po_zip_code, reg_authority_name, reg_first, reg_last, reg_street, reg_city, reg_state, reg_zip_code, reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code, reg_phone, reg_fax, reg_email, reg_website, reg_hours, phone, fax, email, website, hours, review = dogcatcher.begin(voter_state)

	reg_county = reg_county_data[county_data.index(county)]

	#Splits both the reg data and the absentee official data 
	county_data_item = county_data_item_re.findall(county)
	reg_county_data_item = county_data_item_re.findall(reg_county)

	if county_name_re.findall(county)[0].strip() != county_name_re.findall(reg_county)[0].strip():
		print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
		print "The lists don't match. Breaking the code."
		print county, reg_county
		print county_name_re.findall(county)[0], county_name_re.findall(reg_county)[0]
		print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
		sys.exit()

	authority_name = county_data_item[0]
	reg_authority_name = reg_county_data_item[0]
		
	county_name = county_name_re.findall(county)[0].title().replace(" County","")

	official_name = county_data_item[1]
	first_name, last_name, review = dogcatcher.split_name(official_name, review)

	reg_official_name = reg_county_data_item[1]
	reg_first, reg_last, review = dogcatcher.split_name(reg_official_name, review)

	fax = dogcatcher.find_phone(fax_re, county)

	reg_fax = dogcatcher.find_phone(reg_fax_re, reg_county)

	phone = dogcatcher.find_phone(phone_re, county)

	reg_phone = dogcatcher.find_phone(reg_phone_re, reg_county)

	print "_____________________________________"

	#This section finds the address for the absentee official.
	#These are all comma separated, so don't need to rely on the maps API.


	address = county_data_item[2].replace("\r\n", " ").strip()

	comp = csv.reader([address], skipinitialspace=True)
	address_components = comp.next()
	end = len(address_components) - 1

	if suite_re.findall(address_components[end]):
		suite = suite_re.findall(address_components[end])[0]
		address_components[end] = address_components[end].replace(suite,"").strip()
		address_components[end-1] = address_components[end-1] + ", " + suite

	if len(address_components) < 2:
		if po_re.findall(address):

			if po_street_re.findall(address):
				po_street = po_street_re.findall(address)[0]
			else:
				po_street = po_letter_re.findall(address)[0]

			address = address.replace(po_street, "")

			po_zip_code = zip_re.findall(address)[0].strip()
			address = address.replace(po_zip_code, "")

			if not re.search(" \d", address):

				po_city = address.strip()

			else:

				print "There's a broken comma-free address. It'll need to be custom-solved. Have fun!"
				sys.exit()

	elif len(address_components) == 2:
		street = address_components[0]

		if po_re.findall(street):

			if po_street_re.findall(street):
				po_street = po_street_re.findall(street)[0]
			else:
				po_street = po_letter_re.findall(street)[0]

			street = street.replace(po_street,"")

			po_cityzip_components = address_components[1].split()
			po_zip_code = po_cityzip_components.pop()
			po_city = " ".join(po_cityzip_components)

		street = street.strip(" /,")

		if street:
			cityzip = address_components[1]
			cityzip = cityzip.split()
			zip_code = cityzip.pop()
			city = " ".join(cityzip)
		
	elif len(address_components) > 2:

		street = " ".join(address_components[0:end])

		if po_re.findall(street):

			if po_street_re.findall(street):
				po_street = po_street_re.findall(street)[0]
			else:
				po_street = po_letter_re.findall(street)[0]

			street = street.replace(po_street,"")

			po_cityzip_components = address_components[end].split()
			po_zip_code = po_cityzip_components.pop()
			po_city = " ".join(po_cityzip_components)

		street = street.strip(" /")

		if street:
			cityzip = address_components[end]
			cityzip = cityzip.split()
			zip_code = cityzip.pop()
			city = " ".join(cityzip)


	#This section finds the address for the registration official.
	

#////////////////////////////////////////////////

	reg_address = " ".join(reg_county_data_item[2].strip().replace("\r\n", " ").split()).replace(", Texas, ",", ")
	print reg_address


	if re.search("\d,* [A-Z][a-zA-Z]+ \d{5}[\d-]*", reg_address):

		#print reg_address

		if po_re.findall(reg_address):
			if po_street_re.findall(reg_address):
				reg_po_street = po_street_re.findall(reg_address)[0]
			else:
				reg_po_street = po_letter_re.findall(reg_address)[0]

			reg_address = reg_address.replace(reg_po_street, "")
			
			reg_po_zip_code = zip_re.findall(reg_address)[0]

			reg_address = reg_address.replace(reg_po_zip_code, "").strip(", ")

			if re.search("\d[, ]* [A-Z][a-zA-Z]+$", reg_address):

				reg_address_components = re.split("(\d)[, ]* ([A-Z][a-zA-Z]+)$", reg_address)
				end = len(reg_address_components)

				for digit in range(0, end):
					reg_city = " ".join(reg_address_components[end - digit : end])
					if re.search("\d", reg_address_components[end - digit - 1]):
						break

				reg_po_city = reg_city.strip(", ")
				reg_street = "".join(reg_address_components[0 : end - digit])
				reg_zip_code = reg_po_zip_code
				
			elif re.search("\d", reg_address):
				print "You have an address with both a PO box and a street address, and a multi-word city name (maybe)."
				print "This wasn't set up to handle that. Bet you wished you'd written that edge case now, huh?"
				print "The address is: " + reg_address
				sys.exit()
			else:
				reg_po_city = reg_address.strip(", ")

		else:

			cityzip_re_1 = re.compile("\d,* ([A-Z][a-zA-Z]+ \d{5}[\d-]*$)")

			cityzip = cityzip_re_1.findall(reg_address)[0]

			reg_zip_code = zip_re.findall(cityzip)[0]
			
			reg_city = cityzip.replace(reg_zip_code,"").strip(", ")

			reg_street = reg_address.replace(cityzip,"").strip(", ")

	elif re.search(", [A-Z][a-z]+ \d{5}[\d-]*", reg_address):
		
		print reg_address

		if po_re.findall(reg_address):
			if po_street_re.findall(reg_address):
				reg_po_street = po_street_re.findall(reg_address)[0]
			else:
				reg_po_street = po_letter_re.findall(reg_address)[0]

			reg_address_truncated = reg_address.replace(reg_po_street, "").strip("/, .")

			reg_address_truncated_components = re.split("([A-Z][a-z]+ \d{5}[\d-]*$)", reg_address_truncated)

			end = len(reg_address_truncated_components) - 2

			reg_po_cityzip = reg_address_truncated_components[end]
			reg_po_cityzip_components = reg_po_cityzip.partition(" ")

			reg_po_city = reg_po_cityzip_components[0]
			reg_po_zip_code = reg_po_cityzip_components[2]

			if reg_address_truncated_components[end - 1]:
				reg_street = " ".join(reg_address_truncated_components[0:end]).strip(", ")
				reg_city = reg_po_city
				reg_zip_code = reg_po_zip_code

		else:

			reg_address_components = re.split("([A-Z][a-z]+ \d{5}[\d-]*$)", reg_address)

			end = len(reg_address_components) - 2

			reg_cityzip = reg_address_components[end]
			reg_cityzip_components = reg_cityzip.partition(" ")

			reg_street = " ".join(reg_address_components[0:end]).strip(", ")
			reg_city = reg_cityzip_components[0]
			reg_zip_code = reg_cityzip_components[2]

	else:
		reg_comp = csv.reader([reg_address], skipinitialspace=True)
		reg_address_components = reg_comp.next()
		
		
		if po_re.findall(reg_address):
			if po_street_re.findall(reg_address):
				reg_po_street = po_street_re.findall(reg_address)[0]
			else:
				reg_po_street = po_letter_re.findall(reg_address)[0]

		reg_address = " ".join(reg_address.replace(reg_po_street,"").split()).strip(", ")

		if not re.search("\d[A-Za-z,]* [A-Za-z \.,#]+? \d{5}[\d-]*", reg_address):

			#print reg_po_street + " " + reg_address

			reg_po_zip_code = zip_re.findall(reg_address)[0]
			reg_po_city = reg_address.replace(reg_po_zip_code,"")

			# print "Street: " + reg_po_street
			# print "City: " + reg_po_city
			# print "Zip: " + reg_po_zip_code
		else:
			county_test = ""

			# print reg_address

			for words in range(2,reg_address.count(" ")):
				#print reg_address_components

				reg_address_components = reg_address.split()
				end = len(reg_address_components)
				reg_city_try = " ".join(reg_address_components[end - words: end])
				
				base_url = "http://maps.google.com/maps/api/geocode/json?sensor=false&address=%s"
				url = base_url % urllib.quote(reg_city_try)

				place = urllib.urlopen(url)
				json_place = json.load(place)

				if json_place['status'] != "OK":
					continue

				json_address = json_place['results'][0]['address_components']


				for item in json_address:
					if unicode("administrative_area_level_2") in item['types']:
						county_test = item['long_name'].encode('ascii')
					if unicode("locality") in item['types']:
						reg_city = item['long_name'].encode('ascii')
						reg_city = reg_city.replace("Mount ","Mt. ").replace("Saint ","St. ")

				time.sleep(1.5)

				if county_test == county_name:
					break
				elif words == end:
					print "Google can't match this to the right place at all. Fix this edge case. Do not pass go."
					sys.exit()


			reg_address_components = reg_address.partition(reg_city) #in case the city name is also in the street name
			if reg_city in reg_address_components[2]:
				reg_final_components = reg_address_components[2].partition(reg_city)
				reg_street = (" ".join(reg_address_components[0:1]) + reg_final_components[0]).strip(" ")
				reg_zip_code = reg_final_components[2].strip(" ")
			else:
				reg_streetzip = reg_address.replace(reg_city,"").partition("  ")
				reg_street = reg_streetzip[0].strip(", ")
				reg_zip_code = reg_streetzip[2]

			if reg_po_street:
				reg_po_city = reg_city
				reg_po_zip_code = reg_zip_code

	print reg_street + " / " + reg_po_street
	print reg_city + " / " + reg_po_city
	print reg_zip_code + " / " + reg_po_zip_code
	
	
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

dogcatcher.output(result, voter_state, cdir)