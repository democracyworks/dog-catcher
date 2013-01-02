import urllib
import re
import sys
import dogcatcher
import HTMLParser
import os

h = HTMLParser.HTMLParser()

cdir = os.path.dirname(os.path.abspath(__file__)) + "/"

#acquiring the FIPs lists that are necessary later
fips_data_re = re.compile(".+?TX.+?\n")
fips_data = dogcatcher.make_fips_data(fips_data_re)
fips_numbers = dogcatcher.make_fips_numbers(fips_data)
fips_names = dogcatcher.make_fips_names(fips_data)

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

data = data.replace("&quot;","'").replace("&amp;","&").replace(", TX","")
reg_data = reg_data.replace("&quot;","'").replace(", TX","")



county_re = re.compile("<dl>\s*(<dt>.+?</dd>)\s*</dl>", re.DOTALL)
county_data_item_re = re.compile("dd>([^\n]+?\s*[^\n<]*?)\s*<",re.DOTALL)
reg_county_data_item_re = re.compile("dd>(.+?)\s*<", re.DOTALL)
county_name_re = re.compile("<..>([^<>]+?)</dt>")

name_re = re.compile("[^\d]+?")
middle_name_re = re.compile(" ([a-zA-z]\. )")

phone_re = re.compile(">(\(\d{3}\) \d{3}-\d{4}.*?)<")
reg_phone_re = re.compile(">(\(\d{3}\) \d{3}-\d{4}[/ext\.\d ]*).*?<", re.DOTALL)
fax_re = re.compile("FAX: (\(\d{3}\) \d{3}-\d{4})")
reg_fax_re = re.compile("(\(\d{3}\) \d{3}-\d{4}[^>]*?)\n* FAX", re.DOTALL)

zip_re = re.compile("\d{5}[-\d]*")

city_1_re = re.compile("\d ([^,\d]+?) \d{5}[-\d]*") #If the street address ends in a digit and the city is one word, it's very easy to tell where the street address ends.
city_2_re = re.compile(" ([A-Za-z]) [^,\d]+? \d{5}[-\d]*") 
city_3_re = re.compile(", ([^,\d]+?) \d{5}[-\d]*")  #Here, we take the last comma (if there's one with no digits after it) and get everything after it.
city_4_re = re.compile(" ([^,\d]+?) \d{5}[-\d]*") #Here, we just take the last several words without commas or digits. This is not a promising regex.

po_re = re.compile("P\.O\.")
po_letter_re = re.compile("(P\.O\. *[BoxDrawer]+?  *[A-Z])[ ,]") #For the handful of places with "PO Box [A-Z]" in their address.
po_street_re = re.compile("P\.O\. *[BoxDrawer]+?  *\d+")
street_address_re = re.compile(">(.+?) P\.O\.")
street_re = re.compile("(.+),*")

digit_re = re.compile("\d")

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

	fax = dogcatcher.phone_find(fax_re, county)

	reg_fax = dogcatcher.phone_find(reg_fax_re, reg_county)

	phone = dogcatcher.phone_find(phone_re, county)

	reg_phone = dogcatcher.phone_find(reg_phone_re, reg_county)

	#This section finds the address for the registration official.
	#To do so, we first grab the address, which is one of the items in the original breakdown of the official's data.
	#We then try to capture both a PO Box and a PO box/street address combination out of the data. Only zero or one of these things should exist.
	#Here's where things get fun. The addresses are terribly formatted, and the street is on the same line as the city and the zip code, so we can't necessarily tell the end of the street apart from the start of the city.
	#So we try three different regexes to identify cities, based on hand-review of the data. The regexes run in descending order of confidence in the results.
	#(There were originally four, but one was found to be suboptimal and replaced.)
	#Once we have a city, we remove it and the easily-identified zip code from the address, leaving us with whichever of the PO Box and Street Address exist.
	#We run this procedure in three cases: once if there's no PO Box; once if there's both a PO Box and a street address; and once if there's only a PO Box.
	#We also make a mark in "review" to note that there might be a problem with the city if either of the two weak city regexes are used.


	address = county_data_item[2].strip()
	po = po_re.findall(address)
	street_address = street_address_re.findall(county)

	if not po:

		zip_code = zip_re.findall(address)[0]
		if city_1_re.findall(address):
			city = city_1_re.findall(address)[0]
		elif city_2_re.findall(address):
			city = city_2_re.findall(address)[0]
			print address
		elif city_3_re.findall(address):
			city = city_3_re.findall(address)[0]
			review = review + "c"
		else:
			city = city_4_re.findall(address)[0]
			review = review + "c"
		
		street =  street_re.findall(address.replace(city, "").replace(zip_code, ""))[0].rstrip(", ")

	elif street_address:
		if digit_re.search(street_address[0]):

			zip_code = zip_re.findall(address)[0]

			if city_1_re.findall(address):
				city = city_1_re.findall(address)[0]
			elif city_2_re.findall(address):
				city = city_2_re.findall(address)[0]
			elif city_3_re.findall(address):
				city = city_3_re.findall(address)[0]
				review = review + "c"
			else:
				city = city_4_re.findall(address)[0]
				review = review + "c"

			po_street = po_street_re.findall(address.replace(city,"").replace(zip_code,""))[0].rstrip(", ")

			street = street_address[0].rstrip(", ")

		try:
			po_street = po_street_re.findall(address)[0]
		except:
			po_street = po_letter_re.findall(address)[0]

		address = address.replace(po_street,"")

		po_zip_code = zip_re.findall(address)[-1]

		if city_1_re.findall(address):
			po_city = city_1_re.findall(address)[0]
		elif city_2_re.findall(address):
			po_city = city_2_re.findall(address)[0]
			print address
		elif city_3_re.findall(address):
			po_city = city_3_re.findall(address)[0]
			review = review + "c"
		else:
			po_city = city_4_re.findall(address)[0]
			review = review + "c"

	else:
		print address

		try:
			po_street = po_street_re.findall(address)[0]
		except:
			po_street = po_letter_re.findall(address)[0]

		address = address.replace(po_street,"")

		po_zip_code = zip_re.findall(address)[-1]
		if city_1_re.findall(address):
			po_city = city_1_re.findall(address)[0]
		elif city_2_re.findall(address):
			po_city = city_2_re.findall(address)[0]
			print address
		elif city_3_re.findall(address):
			po_city = city_3_re.findall(address)[0]
			review = review + "c"
		else:
			po_city = city_4_re.findall(address)[0]
			review = review + "c"

		# print address

		# po_street = po_street_re.findall(address.replace(po_city,"").replace(po_zip_code,""))[0].rstrip(", ")

	#This section finds the address for the registration official.
	#To do so, we first grab the address, which is one of the items in the original breakdown of the official's data.
	#We then try to capture both a PO Box and a PO box/street address combination out of the data. Only zero or one of these things should exist.
	#Here's where things get fun. The addresses are terribly formatted, and the street is on the same line as the city and the zip code, so we can't necessarily tell the end of the street apart from the start of the city.
	#So we try three different regexes to identify cities, based on hand-review of the data. The regexes run in descending order of confidence in the results.
	#(There were originally four, but one was found to be suboptimal and replaced.)
	#Once we have a city, we remove it and the easily-identified zip code from the address, leaving us with whichever of the PO Box and Street Address exist.
	#We run this procedure in three cases: once if there's no PO Box; once if we think there's both a PO Box and a street address; and once if there's only a PO Box.
	#Within the second case, we may have made an error, so we check to confirm the presence of a street address.
	#We also make a mark in "review" to note that there might be a problem with the city if either of the two weak city regexes are used.

	address = reg_county_data_item[2].strip()
	reg_po = po_re.findall(address)
	reg_street_address = street_address_re.findall(reg_county)
	if county_name == "Lampasas":
		address = "407 S. Pecan P.O. Box 571, Lampasas 76550"

	if not reg_po:
		reg_zip_code = zip_re.findall(address)[0]

		if city_1_re.findall(address):
			reg_city = city_1_re.findall(address)[0]
		elif city_3_re.findall(address):
			reg_city = city_3_re.findall(address)[0]
			review = review + "d"
		else:
			reg_city = city_4_re.findall(address)[0]
			review = review + "d"

		reg_street =  street_re.findall(address.replace(reg_city, "").replace(reg_zip_code, ""))[0].rstrip(", ")

	elif reg_street_address:
		if digit_re.search(reg_street_address[0]):

			reg_zip_code = zip_re.findall(address)[-1]

			if city_1_re.findall(address):
				reg_city = city_1_re.findall(address)[0]
			elif city_3_re.findall(address):
				reg_city = city_3_re.findall(address)[0]
				review = review + "d"
			else:
				reg_city = city_4_re.findall(address)[0]
				review = review + "d"

			reg_po_street = po_street_re.findall(address.replace(reg_city,"").replace(reg_zip_code,""))[0].rstrip(", ")
			reg_street = reg_street_address[0].rstrip(", ")

		try:
			reg_po_street = po_street_re.findall(address)[0]
		except:
			reg_po_street = po_letter_re.findall(address)[0]

		address = address.replace(reg_po_street,"")

		reg_po_zip_code = zip_re.findall(address)[-1]

		if city_1_re.findall(address):
			reg_po_city = city_1_re.findall(address)[0]
		elif city_3_re.findall(address):
			reg_po_city = city_3_re.findall(address)[0]
			review = review + "d"
		else:
			reg_po_city = city_4_re.findall(address)[0]
			review = review + "d"

	else:

		print address

		try:
			reg_po_street = po_street_re.findall(address)[0]
		except:
			reg_po_street = po_letter_re.findall(address)[0]

		address = address.replace(reg_po_street,"")

		reg_po_zip_code = zip_re.findall(address)[0]
		
		if city_1_re.findall(address):
			reg_po_city = city_1_re.findall(address)[0]
		elif city_3_re.findall(address):
			reg_po_city = city_3_re.findall(address)[0]
			review = review + "d"
		else:
			reg_po_city = city_4_re.findall(address)[0]
			review = review + "d"


	#Fixing a known error in Winkler County.
	if reg_po_street == "PO Drawer Kermit":
		reg_po_street = "PO BOX 1065"
		reg_po_city = "KERMIT"
		reg_po_zip = "79745"
	

	
	
	fips = dogcatcher.fips_find(county_name, fips_names, fips_numbers)

	result.append([authority_name, first_name, last_name, county_name, fips,
	street, city, address_state, zip_code,
	po_street, po_city, po_state, po_zip_code,
	reg_authority_name, reg_first, reg_last,
	reg_street, reg_city, reg_state, reg_zip_code,
	reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code,
	reg_phone, reg_fax, reg_email, reg_website, reg_hours,
	phone, fax, email, website, hours, voter_state, source, review])

#This outputs the results to a separate text file.

output = open(cdir + "texas.txt", "w")
for r in result:
	r = h.unescape(r)
	output.write("\t".join(r))
	output.write("\n")
output.close()