import sys
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

voter_state = "MI"
source = "State"

result = [("authority_name", "first_name", "last_name", "county_name", "fips",
    "street", "city", "address_state", "zip_code",
    "po_street", "po_city", "po_state", "po_zip_code",
    "reg_authority_name", "reg_first", "reg_last",
    "reg_street", "reg_city", "reg_state", "reg_zip_code",
    "reg_po_street", "reg_po_city", "reg_po_state", "reg_po_zip_code",
    "reg_phone", "reg_fax", "reg_email", "reg_website", "reg_hours",
    "phone", "fax", "email", "website", "hours", "voter_state", "source", "review")]

#We need to obtain a list of county clerks and of municipal clerks.
#Each county page has a list of municipal pages.
#So we acquire every county page and clean it.
#In the process of cleaning it, we extract the full list of municipal pages.
#We then access each of those pages and clean them.
#And then we're done. Whee!

#Every county is a different item in a dropdown menu, so we have to cycle through them all.
#To do so, we grab the dropdown menu, extract a list of counties, then grab a series of web pages based on that list.
#This grabs a page containing a list of PA counties and writes it to a file. Writing it isn't strictly necessary, but saves some run time in the long run.
#We save separate lists of county names and county references because the references used in the dropdown menus are different from the county's names.

county_list_re = re.compile("<option value=\"(.+?)\">.+? County</option>")
county_name_re = re.compile("<option value=\".+?\">(.+?) County</option>")
output_path = "C:\Users\pkoms\Documents\TurboVote\Scraping\michigan-counties.html"

url = "https://webapps.sos.state.mi.us/mivote/ClerkSearch.aspx"
data = urllib.urlopen(url).read()
output = open(output_path,"w")
output.write(data)
output.close()

county_list = county_list_re.findall(data)
county_names = county_name_re.findall(data)

#This uses the mechanize package to submit every item in county_list--the list of county names as used in the menu--and grab and save a webpage for each one.

trim_re = re.compile("(<td valign=\"top\">.+)\s+</tr>\s+</table>\s+</div>\s+</td>", re.DOTALL)

# for county in county_list:
# 	print county

	
# 	br = mechanize.Browser() #Creates a mechanize browser object.
# 	br.set_handle_robots(False) # ignore robots.txt
# 	br.open(url) #Opens the page.
# 	br.select_form(name = "aspnetForm") #The drop-down menu is titled aspnetForm.
# 	br["ctl00$ContentPlaceHolder1$csCnty"] = [county,] #It takes an input called ctl00$ContentPlaceHolder1$csCnty.
# 	res = br.submit() #res is the resulting page when we submit the inputs from earlier
# 	content = res.read() #this creates a string of the page.
# 	trimmed_content = trim_re.findall(content)[0] #this trims the page down to only what we need.
# 	#This writes the page to a file.
# 	file_path = cdir + county + "-MI-clerks.html"
# 	output = open(file_path,"w")
# 	output.write(trimmed_content)
# 	output.close()

#output_path points to a file in which we'll insert a trimmed version of the data in each michigan county.
#Once we have that file, we'll break it down into each county and extract data out of each of those.



output_path = cdir + "michigan-county-clerks.html"

clerks = open(output_path,"w")
clerks.write("")
clerks.close
clerks = open(output_path,"a")



for county in county_list:
	file_path = cdir + county + "-mi-clerks.html"
	data = open(file_path).read()

 	clerks.write(data)

clerks.close()

data = open(output_path).read()

county_data_re = re.compile("<td valign=\"top\">.+?</td>", re.DOTALL)

county_data = county_data_re.findall(data)

official_name_re = re.compile("ClerkorLocationName.+?class=\"clerkText\">(.+?)</span>")

phone_re = re.compile("Ph:(.+?)</span>")
fax_re = re.compile("Fax:(.+?)</span>")

address_re = re.compile("Address\" class=\"clerkText\">(.+?)</span><br />", re.DOTALL)

csz_re = re.compile("CityStateZip.+?>(.+?)</span><br />")
city_re = re.compile("(.+?) [A-Z][A-Z]")
state_re = re.compile(" ([A-Z][A-Z]) ")
zip_re = re.compile(" (\d{5}[\d-]*)")
po_re = re.compile("(P[oO] Box .+) *", re.DOTALL)
email_re = re.compile("Email: (.+?) *<")

municipal_re = re.compile("href=\"LocalClerk\.aspx\?jd=(\d{5})")

municipality_list = []

for county in county_data:

	authority_name, first_name, last_name, county_name, town_name, fips, street, city, address_state, zip_code, po_street, po_city, po_state, po_zip_code, reg_authority_name, reg_first, reg_last, reg_street, reg_city, reg_state, reg_zip_code, reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code, reg_phone, reg_fax, reg_email, reg_website, reg_hours, phone, fax, email, website, hours, review = dogcatcher.begin(voter_state)

	county_name = county_names[county_data.index(county)].strip()
	
	official = official_name_re.findall(county)[0]

	first_name, last_name, official_name, review = dogcatcher.make_name(official, ",", review)

	email = dogcatcher.find_emails(email_re, county)
	phone = dogcatcher.phone_find(phone_re, county)
	fax = dogcatcher.phone_find(fax_re, county)

	#This section finds the address. After finding the address, it identifies a city/state/zip (csz) combination and a PO Box number if that exists.
    #It removes both the CSZ and the PO Address (if it exists) from the full address, leaving behind a street address with some garbage.
    #It then cleans up the street address and pulls the city, state, and zip out of the csz, and assigns them as appropriate to the street address and state.

	address = address_re.findall(county)[0]

	csz = csz_re.findall(county)[0]

	try:
		po_street = po_re.findall(address)[0].replace(csz,"").strip(", ")
	except:
		po_street = ""

	street = address.replace(po_street,"").replace(csz,"")
	street = street.replace("\n",", ").replace("\r","").replace(" ,",",").strip(" ,")

	if po_street:
		po_city = city_re.findall(csz)[0].strip()
		po_state = state_re.findall(csz)[0].strip()
		po_zip_code = zip_re.findall(csz)[0].strip()
	if street:
		city = city_re.findall(csz)[0].strip()
		address_state = state_re.findall(csz)[0].strip()
		zip_code = zip_re.findall(csz)[0].strip()

	if county_name == "Wayne" and street == "2 Woodward Ave":
		street = street + " Suite 502"

	fips = dogcatcher.fips_find(county_name, voter_state)

	result.append([authority_name, first_name, last_name, county_name, fips,
	street, city, address_state, zip_code,
	po_street, po_city,	po_state, po_zip_code,
	reg_authority_name, reg_first, reg_last,
	reg_street, reg_city, reg_state, reg_zip_code,
	reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code,
	reg_phone, reg_fax, reg_email, reg_website, reg_hours,
	phone, fax, email, website, hours, voter_state, source, review])

#This outputs the results to a separate text file.

output = open(cdir + "michigan-counties.txt", "w")
for r in result:
	r = h.unescape(r)
	output.write("\t".join(r))
	output.write("\n")
output.close()

municipality_list = municipal_re.findall(data)
print municipality_list








#Note that in MI, we give an unusual item: town_name_full. This is the town name, but with "Township" or "City of" included.
#This is necessary because, in at least one county, there is a city and a county by the same name.

result = [("authority_name", "first_name", "last_name", "town_name", "county_name", "fips",
    "street", "city", "address_state", "zip_code",
    "po_street", "po_city", "po_state", "po_zip_code",
    "reg_authority_name", "reg_first", "reg_last",
    "reg_street", "reg_city", "reg_state", "reg_zip_code",
    "reg_po_street", "reg_po_city", "reg_po_state", "reg_po_zip_code",
    "reg_phone", "reg_fax", "reg_email", "reg_website", "reg_hours",
    "phone", "fax", "email", "website", "hours", "voter_state", "source", "review", "town_name_full")]





town_data_re = re.compile("<span id=\"ctl00_ContentPlaceHolder1_lblCounty\".+?</td>\s", re.DOTALL)

town_name_re = re.compile("display:inline-block;\">(.+?)</span>")

county_name_re = re.compile("class=\"countyName\">(.+?)</span>")

address_re = re.compile("Address\" class=\"clerkText\">(.+?)</span><br />\s+<span id=\"ctl00_ContentPlaceHolder1_lblCityStateZip\"", re.DOTALL)

po_re = re.compile("<span ID=\"lblAddress2\" Class=\"clerkText\">(.+)")

for town_id in municipality_list:

	print town_id

	authority_name, first_name, last_name, county_name, town_name, fips, street, city, address_state, zip_code, po_street, po_city, po_state, po_zip_code, reg_authority_name, reg_first, reg_last, reg_street, reg_city, reg_state, reg_zip_code, reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code, reg_phone, reg_fax, reg_email, reg_website, reg_hours, phone, fax, email, website, hours, review = dogcatcher.begin(voter_state)

	#The URLs are uniformly formatted; we insert every URL suffix on municipality_list into the URL format, and then grab and save a webpage based on that.
	#(Writing it to a file isn't strictly necessary, but saves some time down the line.)

	file_name = cdir + town_id + "-MI-municipal-clerks.html"

	#To be used when part of the data has already been extracted.
	try:
		data = open(file_name).read()

		town = data
	except:
		town_url = "https://webapps.sos.state.mi.us/mivote/LocalClerk.aspx?jd=" + town_id


		data = urllib.urlopen(town_url).read()
		output = open(file_name,"w")
		output.write(data)
		output.close()

		town = town_data_re.findall(data)[0]

		data = open(file_name).read()

	# #To be used when collecting a fresh set of data.
	# town_url = "https://webapps.sos.state.mi.us/mivote/LocalClerk.aspx?jd=" + town_id

	# data = urllib.urlopen(town_url).read()
	# output = open(file_name,"w")
	# output.write(data)
	# output.close()

	# town = town_data_re.findall(data)[0]

	# data = open(file_name).read()
	


	authority_name, first_name, last_name, county_name, town_name, fips, street, city, address_state, zip_code, po_street, po_city, po_state, po_zip_code, reg_authority_name, reg_first, reg_last, reg_street, reg_city, reg_state, reg_zip_code, reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code, reg_phone, reg_fax, reg_email, reg_website, reg_hours, phone, fax, email, website, hours, review = dogcatcher.begin(voter_state)

	authority_name = "Clerk"

	town_name_full = town_name_re.findall(town)[0].strip()
	town_name = town_name_full.replace("City of","").replace("Township","").strip()

	county_name = county_name_re.findall(town)[0].replace("County","").strip()

	official_name = official_name_re.findall(town)[0].partition(",")[0]
	first_name, last_name, review = dogcatcher.split_name(official_name, review)

	email = dogcatcher.find_emails(email_re, county)
	phone = dogcatcher.phone_find(phone_re, county)
	fax = dogcatcher.phone_find(fax_re, county)

	#There are many known errors in both phone numbers or fax numbers. This fixes them.
	#They're currently commented out because they don't work well with phone_find as written.

	# if town_name == "Fayette" or phone == "357-4145":
	# 	phone = "517-" + phone
	# if "906 906" in phone:
	# 	phone.replace("906 ","",1)
	# elif county_name == "Lenawee" and town_name == "Franklin":
	# 	fax = "517-431-2320"
	# if town_name == "Fayette" or fax == "458-2390":
	# 	fax = "517-" + fax
	# elif county_name == "Lenawee" and town_name == "Franklin":
	# 	fax = "517-431-2320"
	# elif town_name == "Hamtramck":
	# 	fax = "313-876-7703"
	
	#A few towns don't have addresses listed; this catches them before we try to clean addresses from them.

	if "Address\" class=\"clerkText\"><" in town:
		address = ""

	#This section finds the full address. After finding the address, it identifies a city/state/zip (csz) combination and a PO Box number if that exists.
    #It removes both the CSZ and the PO Address (if it exists) from the full address, leaving behind a street address with some garbage.
    #It then cleans up the street address and pulls the city, state, and zip out of the csz, and assigns them as appropriate to the street address and state.

	else:
		address = address_re.findall(town)[0]

	csz = csz_re.findall(town)[0]

	try:
		po_street = po_re.findall(address)[0].strip(", ")
	except:
		po_street = ""

	street = address.replace(po_street,"").replace("</span><br><span ID=\"lblAddress2\" Class=\"clerkText\">","")
	street = street.replace("\n",", ").replace("\r","").replace(" ,",",").strip(" ,")

	#I don't remember how or why I found these corrections, but they all seem to be accurate.

	if town_name_full == "Jefferson Township" and county_name == "Cass":
		street = "24725 Jefferson Center Street"
		po_street = "P.O. Box 188"
	elif town_name_full == "Au Gres Township" and county_name == "Arenac":
		street = "1865 South Swenson Road"
	elif town_name_full == "Crystal Township" and county_name == "Montcalm":
		po_street = "PO Box 358"
	elif town_name_full == "Geneva Township" and county_name == "Midland":
		street = "3704 W Barden Rd"
	elif town_name_full == "Whiteford Township" and county_name == "Monroe":
	 	street = "8000 Yankee Rd, Ste 100"
	elif town_name_full == "Swan Creek Township" and county_name == "Saginaw":
		street = "11415 Lakefield Rd"
		po_street = "P.O. Box 176"
	elif town_name_full == "Star Township" and county_name == "Antrim":
		po_street = "P.O. Box 94"
	elif town_name_full == "Sherman Township" and county_name == "Gladwin":
		street = "4013 Oberlin Rd"
	elif town_name_full == "Sanilac Township" and county_name == "Sanilac":
		po_street = "P.O. Box 631"
		street = "20 N. Ridge Street"
	elif town_name_full == "Mullett Township" and county_name == "Cheboygan":
		po_street = "P.O. Box 328"
	elif town_name_full == "Houghton Township" and county_name == "Keweenaw":
		street = "5059 Fourth Street"
	elif town_name_full == "Greenland Township" and county_name == "Ontonagon":
		po_street = "P.O. Box 204"
		street = "1502 Mass Avenue"

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

	print [address]

	fips = dogcatcher.fips_find(county_name, voter_state)
	
	result.append([authority_name, first_name, last_name, town_name, county_name, fips,
	street, city, address_state, zip_code,
	po_street, po_city,	po_state, po_zip_code,
	reg_authority_name, reg_first, reg_last,
	reg_street, reg_city, reg_state, reg_zip_code,
	reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code,
	reg_phone, reg_fax, reg_email, reg_website, reg_hours,
	phone, fax, email, website, hours, voter_state, source, review, town_name_full])

#This outputs the results to a separate text file.

output = open(cdir + "michigan-cities.txt", "w")
for r in result:
	r = h.unescape(r)
	output.write("\t".join(r))
	output.write("\n")
output.close()