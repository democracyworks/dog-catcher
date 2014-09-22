import urllib
import re
import sys
import dogcatcher
import HTMLParser
import os
import urllib2
import mechanize

voter_state = "VA"
source = "State"

h = HTMLParser.HTMLParser()

cdir = os.path.dirname(os.path.abspath(__file__)) + "/"
tmpdir = cdir + "tmp/"
#Every county is a different item in a dropdown menu, so we have to cycle through them all.
#To do so, we grab the dropdown menu, extract a list of counties, then grab a series of web pages based on that list.
#This grabs a page containing a list of GA counties and writes it to a file. Writing it isn't strictly necessary, but saves some run time in the long run.

file_path = tmpdir + "va-counties.html"
url = "https://www.voterinfo.sbe.virginia.gov/PublicSite/Public/FT2/PublicContactLookup.aspx"

data = urllib.urlopen(url).read()
output = open(file_path,"w")
output.write(data)
output.close()

data = open(file_path).read().replace("&amp;","and")

#This extracts a list of option titles as referred to in the HTML of the drop-down menu from the webpage grabbed earlier

county_list_re = re.compile("option value=\"(.+?)\"")
county_name_re = re.compile("option value=\".+?\">(.+?)<")
county_list = county_list_re.findall(data)
county_names = county_name_re.findall(data)

trim_re = re.compile("Voter Registration Office Contact Information.+?\s+</td>\s+</tr>\s+</div>\s+</div>\s+</table>", re.DOTALL)
space_re = re.compile("\n\s+")
break_re = re.compile("<[/tablerd]+>[<>/tablerd\s]+<[/tablerd]+>")

#This uses the mechanize package to submit every item in county_list--the list of county names as used in the menu--and grab a webpage based on each one.

final_data = ""
file_path = tmpdir + "va-clerks.html"

for county in county_list:

	print county

	br = mechanize.Browser() #Creates a mechanize browser object.
	br.set_handle_robots(False) # ignore robots
	br.open(url) #Opens the page.
	br.select_form(name = "aspnetForm") #The drop-down menu is titled form1.
	br["ctl00$ContentPlaceHolder1$usrCounty$cboCounty"] = [county,] #It takes an input called ctl00$ContentPlaceHolder1$usrCounty$cboCounty.
	res = br.submit() #res is the resulting page when we submit the inputs from earlier
	content = res.read() #this creates a string of the page.
	trimmed_content = trim_re.findall(content)[0] #this trims the page down to only what we need.
	for item in break_re.findall(trimmed_content):
		trimmed_content = trimmed_content.replace(item,"")
	for item in space_re.findall(trimmed_content):
		trimmed_content = trimmed_content.replace(item,"\t\n")
	trimmed_content = trimmed_content.replace("\r","").replace("ctl00_ContentPlaceHolder1_usrLocalityRegContact","")
	final_data = final_data + trimmed_content


output = open(file_path,"w")
output.write(final_data)
output.close()

county_result = [("authority_name", "first_name", "last_name", "county_name", "fips",
    "street", "city", "address_state", "zip_code",
    "po_street", "po_city", "po_state", "po_zip_code",
    "reg_authority_name", "reg_first", "reg_last",
    "reg_street", "reg_city", "reg_state", "reg_zip_code",
    "reg_po_street", "reg_po_city", "reg_po_state", "reg_po_zip_code",
    "reg_phone", "reg_fax", "reg_email", "reg_website", "reg_hours",
    "phone", "fax", "email", "website", "hours", "voter_state", "source", "review")]

city_result = [("authority_name", "first_name", "last_name", "town_name", "fips",
    "street", "city", "address_state", "zip_code",
    "po_street", "po_city", "po_state", "po_zip_code",
    "reg_authority_name", "reg_first", "reg_last",
    "reg_street", "reg_city", "reg_state", "reg_zip_code",
    "reg_po_street", "reg_po_city", "reg_po_state", "reg_po_zip_code",
    "reg_phone", "reg_fax", "reg_email", "reg_website", "reg_hours",
    "phone", "fax", "email", "website", "hours", "voter_state", "source", "review")]


county_re = re.compile("Voter Registration Office Contact Information.+?(?=Voter Registration Office Contact Information)", re.DOTALL)

name_re = re.compile("<span id=\"_lblGeneralRegistrar\" class=\"lblDisplay\">(.+?)</span>")

phone_re = re.compile("Phone:.+?(\d{3}-\d{3}.+?)<", re.DOTALL)
fax_re = re.compile("Fax:.+?(\d{3}-\d{3}.+?)<", re.DOTALL)
email_re = re.compile("Email:.+?>(.+?@.+?)<", re.DOTALL)
website_re = re.compile("DarkSlateBlue\">(.+?)</font")

mailing_address_re = re.compile("Mailing Address</span>.+?lblZipText.+?<span", re.DOTALL)
address_re = re.compile("Physical Address:.+?</div", re.DOTALL)

street_re = re.compile("Address line #\d.+?>([^<>]*?\d[^<>]+?)<")
po_re = re.compile(">(P[ \.]*O .+?)<")

city_re = re.compile("lblCity.+?>(.+?)</span")
state_re = re.compile("usrState_lblView.+?>(.+?)</span")
zip_re = re.compile("usrZipCode.+?>(.+?)</span")

data = open(file_path).read().replace("&Amp;","and")

county_list = county_re.findall(data)

for county in county_list:

	authority_name, first_name, last_name, county_name, town_name, fips, street, city, address_state, zip_code, po_street, po_city, po_state, po_zip_code, reg_authority_name, reg_first, reg_last, reg_street, reg_city, reg_state, reg_zip_code, reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code, reg_phone, reg_fax, reg_email, reg_website, reg_hours, phone, fax, email, website, hours, review = dogcatcher.begin(voter_state)

	county_name = county_names[county_list.index(county)].title().replace(" County","")

	authority_name = "Voter Registration Office"

	print "______________________________________________________________________\n" + county_name


	try:
		name = name_re.findall(county)[0]
	except:
		name = ""

	first_name, last_name, review = dogcatcher.split_name(name, review)

	mailing_address = mailing_address_re.findall(county)[0]

	try:
		po_street = po_re.findall(mailing_address)[0].strip()
	except:
		po_street = ""

	street = ""

	for item in street_re.findall(mailing_address):
		street = (street + ", " + item).strip(", ")

	street = street.replace(po_street, "").replace(", , ",", ").strip(", ")


	if street:
	 	city = city_re.findall(mailing_address)[0].strip()
	 	address_state = state_re.findall(mailing_address)[0].strip()
	 	zip_code = zip_re.findall(mailing_address)[0].strip()
	 	if po_street:
	 		po_city = city
	 		po_state = address_state
	 		po_zip_code = zip_code
	else:
	 	po_city = city_re.findall(mailing_address)[0].strip()
		po_state = state_re.findall(mailing_address)[0].strip()
	 	po_zip_code = zip_re.findall(mailing_address)[0].strip()



	if not street or not po_street: #if either a street address or PO Box is missing, we might be able to find it in the main address.
		address_all = address_re.findall(county) #not all counties have a regular address, so we need to check for that.
		if not address_all:
			pass
		else:
			address = address_all[0]
			street_all = street_re.findall(address)
			if street_all == street_re.findall(mailing_address): #some of the counties' regular addresses are identical to the mailing address.
				pass
			else:
				if not po_street and po_re.findall(address):
					po_street = po_re.findall(address)[0]
					po_city = city_re.findall(address)[0].strip()
					po_state = state_re.findall(address)[0].strip()
	 				po_zip_code = zip_re.findall(address)[0].strip()


				elif not street and street_all:


					street = ""

					for item in street_all:
						street = (street + ", " + item).strip(", ")

						street = street.replace(po_street, "").replace(", , ",", ").strip(", ")

						city = city_re.findall(address)[0].strip()
						address_state = state_re.findall(address)[0].strip()
						zip_code = zip_re.findall(address)[0].strip()



	print street + ", " + city + ", " + address_state + " " + zip_code

	print po_street + ", " + po_city + ", " + po_state + " " + po_zip_code


	phone = dogcatcher.find_phone(phone_re, county)
	fax = dogcatcher.find_phone(fax_re,county)
	email = dogcatcher.find_emails(email_re, county)

	try:
		if county_name == "Staunton City":
			website = "http://www.staunton.va.us/directory/departments-h-z/registrar/how-to-vote"
		else:
			website = dogcatcher.website_find(website_re, county)
	except:
		website = ""

	fips = dogcatcher.find_fips(county_name, voter_state)


	county_result.append([authority_name, first_name, last_name, county_name, fips,
	street, city, address_state, zip_code,
	po_street, po_city, po_state, po_zip_code,
	reg_authority_name, reg_first, reg_last,
	reg_street, reg_city, reg_state, reg_zip_code,
	reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code,
	reg_phone, reg_fax, reg_email, reg_website, reg_hours,
	phone, fax, email, website, hours, voter_state, source, review])

dogcatcher.output(county_result, voter_state, cdir)
