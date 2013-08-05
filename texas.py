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

url = "http://www.sos.state.tx.us/elections/voter/county.shtml"
data = urllib.urlopen(url).read()
output = open(file_path,"w")
output.write(data)
output.close()

reg_url = "http://www.sos.state.tx.us/elections/voter/votregduties.shtml"
reg_data = urllib.urlopen(reg_url).read()
output = open(reg_file_path,"w")
output.write(reg_data)
output.close()

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

zip_re = re.compile("(?<!\d)\d{5}(?!\d)[-\d]*")

city_1_re = re.compile("\d ([^,\d]+?) \d{5}[-\d]*") #If the street address ends in a digit and the city is one word, it's very easy to tell where the street address ends.
city_2_re = re.compile(" ([A-Za-z]) [^,\d]+? \d{5}[-\d]*") 
city_3_re = re.compile(", ([^,\d]+?) \d{5}[-\d]*")  #Here, we take the last comma (if there's one with no digits after it) and get everything after it.
city_4_re = re.compile(" ([^,\d]+?) \d{5}[-\d]*") #Here, we just take the last several words without commas or digits. This is not a promising regex.

po_re = re.compile("PO ")
po_letter_re = re.compile("(PO [BD].+?[xr]  *[A-Z])[ ,]") #For the handful of places with "PO Box [A-Z]" in their address.
po_street_re = re.compile("PO [BD].+?[xr] *\d+")
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


	address = county_data_item[2].strip().replace("\r\n", " ")

	po = po_re.findall(address)

	street = address.replace(po_street, "").strip(" \n,").replace("\n", ", ").replace(" ,", ",")
		
	try:
		po_street = po_re.findall(address)[0]
	except:
		po_street = ""

	if po_street_re.findall(address):
		po_street = po_street_re.findall(address)[0]
	elif po_letter_re.findall(address):
		po_street = po_letter_re.findall(address)[0]
	
	street = address.replace(po_street,"")
	
	if po_street is not "":
		po_city = address.replace(po_street, "").strip(" \n,").replace("\n", ", ").replace(" ,", ",")
		street = address.replace(address, "")
		cityzip = po_city.split(" ")  #This separates out the city and zip code
		po_zip_code = cityzip.pop() #Pop the last part off, which should always be the zip code
		po_city = ' '.join(cityzip) #Restring the rest, which should be the city.
		
    #Dealing with the counties with PO box/Street address
	if re.search("/", po_city) is not None and po_city is not "":
		strtsplit = po_city.split(" ")
		po_city = strtsplit.pop()
		city = po_city
		street = " ".join(strtsplit)
		street = re.sub("[^A-Za-z0-9. ]+", "", street)
		
	comp = csv.reader([street], skipinitialspace=True)
	for c in comp:
		if len(c)==2:
			street = c[0]
			cityzip = c[1]
			cityzip = cityzip.split(" ")
			zip_code = cityzip.pop()
			city = ' '.join(cityzip)
			
		if len(c)>2:
			street = c[0] +" "+ c[1]
			cityzip = c[2]
			cityzip = cityzip.split(" ")
			zip_code = cityzip.pop()
			city = ' '.join(cityzip)
	
	#This block of code is for when there isn't a comma between the Suite number and the city		
	if re.search("Ste", city) is not None and re.search("Stephenville", city) is None:
		citysplit = city.split(" ")
		cityste = []
		for c in citysplit:
			if len(c) > 0:
				cityste.append(c)
		street = street +" "+ cityste[0] +" "+ cityste[1]
		city = str(cityste[2])
		if len(cityste)==4:
			city = city +" "+ str(cityste[3]) 


	#fixing known problems		
	if county_name == "Hamilton":
		address = "Hamilton 76531"
		street = "102 N Rice St #112"
	if county_name == "Scurry":
		address = "Snyder 79549"
		street = "1806 25th St #300"
		
	#print [address]

	base_url = "http://maps.google.com/maps/api/geocode/json?sensor=false&address=%s"
	
	url = base_url % urllib.quote(address)

	place = urllib.urlopen(url)
	json_place = json.load(place)



	if json_place['status'] != "OK":
		print json_place
		print "Egad! %s" % address
		sys.exit()

	#At this point, we're looking for the full name of Administrative Area 2 (County). So we cycle through components of the JSON until we find it.

	subpremise = ""
	street_number = ""
	route = ""

	json_address = json_place['results'][0]['address_components']
	print address
	print json_address

	for item in json_address:
		if unicode("subpremise") in item['types']:
			subpremise = item['long_name'].encode('ascii')
		if unicode("street_number") in item['types']:
			street_number = item['long_name'].encode('ascii')
		if unicode("route") in item['types']:
			route = item['long_name'].encode('ascii')
		if unicode("locality") in item['types']:
			city = item['long_name'].encode('ascii')
		if unicode("postal_code") in item['types']:
			zip_code = item['long_name'].encode('ascii')

	if route:
		if subpremise:
			street = street_number + " " + route + " #" + subpremise
		else:
			street = street_number + " " + route

	if po_street:
		po_city = reg_city
		zip_code = reg_po_zip_code
		if not street:
			city = ""
			zip_code = ""


	time.sleep(1.5)

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

	address = reg_county_data_item[2].strip().replace("\r\n", " ")
	if county_name == "Lampasas":
		address = "407 S. Pecan P.O. Box 571, Lampasas 76550"
	if "278 Roby 76543" in address:
		address = address.replace("76543", "79543")
	if county_name == "Hamilton":
		address = "Hamilton 76531"
		reg_street = "102 N Rice St #112"
	if county_name == "Scurry":
		address = "Snyder 79549"
		reg_street = "1806 25th St #300"

	print [address]

	if po_street_re.findall(address):
		reg_po_street = po_street_re.findall(address)[0]
	elif po_letter_re.findall(address):
		reg_po_street = po_letter_re.findall(address)[0]
	

	address = address.replace(reg_po_street,"")

	print [address]

	base_url = "http://maps.google.com/maps/api/geocode/json?sensor=false&address=%s"
	
	url = base_url % urllib.quote(address)

	place = urllib.urlopen(url)
	json_place = json.load(place)



	if json_place['status'] != "OK":
		print json_place
		print "Egad! %s" % address
		sys.exit()

	#At this point, we're looking for the full name of Administrative Area 2 (County). So we cycle through components of the JSON until we find it.

	subpremise = ""
	street_number = ""
	route = ""

	json_address = json_place['results'][0]['address_components']
	print address
	print json_address

	for item in json_address:
		if unicode("subpremise") in item['types']:
			subpremise = item['long_name'].encode('ascii')
		if unicode("street_number") in item['types']:
			street_number = item['long_name'].encode('ascii')
		if unicode("route") in item['types']:
			route = item['long_name'].encode('ascii')
		if unicode("locality") in item['types']:
			reg_city = item['long_name'].encode('ascii')
		if unicode("postal_code") in item['types']:
			reg_zip_code = item['long_name'].encode('ascii')

	if route:
		if subpremise:
			reg_street = street_number + " " + route + " #" + subpremise
		else:
			reg_street = street_number + " " + route

	if reg_po_street:
		reg_po_city = reg_city
		reg_zip_code = reg_po_zip_code
		if not reg_street:
			reg_city = ""
			reg_zip_code = ""


	time.sleep(1.5)




	print [reg_street]
	print [reg_po_street]
	print [reg_city]
	print [reg_zip_code]

	#Fixing a known error in Winkler County.
	if reg_po_street == "PO Drawer Kermit":
		reg_po_street = "PO BOX 1065"
		reg_po_city = "KERMIT"
		reg_po_zip = "79745"

	
	
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
