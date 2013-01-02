
def begin(state):
	"This function sets null values for almost every variable, and sets all of the Address/State values to the state to begin with."
	street = ""
	po_street = ""
	city = ""
	address_state = state
	zip_code = ""
	po_city = ""
	po_state = state
	po_zip_code = ""
	fips = ""
	first_name = ""
	last_name = ""
	authority_name = ""
	phone = ""
	fax = ""
	email = ""
	website = ""
	hours = ""
	reg_street = ""
	reg_city = "" 
	reg_state = state
	reg_zip_code = ""
	reg_po_street = ""
	reg_po_city = ""
	reg_po_state = state
	reg_po_zip_code = ""
	reg_authority_name = ""
	reg_first = ""
	reg_last = ""
	reg_phone = ""
	reg_fax = ""
	reg_email = ""
	reg_website = ""
	reg_hours = ""
	town_name = ""
	review = ""
	county_name = ""

	return authority_name, first_name, last_name, county_name, town_name, fips, street, city, address_state, zip_code, po_street, po_city, po_state, po_zip_code, reg_authority_name, reg_first, reg_last, reg_street, reg_city, reg_state, reg_zip_code, reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code, reg_phone, reg_fax, reg_email, reg_website, reg_hours, phone, fax, email, website, hours, review


def make_fips_data(state_re):
	"breaks the raw FIPS data into a list of county/state/number triples."

	import os

	cdir = os.path.dirname(os.path.abspath(__file__)) + "/"

	fips_path = cdir + "fips.txt"

	fips_all = open(fips_path).read()

	fips_data = state_re.findall(fips_all)

	return fips_data


def make_fips_numbers(fips_data):
	"takes a list of FIPs county/state/number triples and generates a list of FIPS numbers in order."	

	import re

	fips_numbers_re = re.compile("\d+")
	fips_numbers = []
	
	for fip in fips_data:
		fips_numbers.append(fips_numbers_re.findall(fip)[0])

	return fips_numbers


def make_fips_names(fips_data):
	"takes a list of FIPs county/state/number triples and generates a list of county names in order."

	import re

	fips_names_re = re.compile("(.+?)\t")
	fips_names = []

	for fip in fips_data:
		fips_names.append(fips_names_re.findall(fip)[0])

	return fips_names


def fips_find(county_name, fips_names, fips_numbers):
	"takes a county name and identifies its associated FIPS value"

	if "St " in county_name:
		county_name = county_name.replace("St ","St. ")

	for fips_name in fips_names:
		if county_name.lower() == fips_name.lower():
			fips = fips_numbers[fips_names.index(fips_name)]
			break

	return fips

def insert(original, new, pos):
	"Inserts a string into a larger string."
	return original[:pos] + new + original[pos:]


def phone_find(phone_re, county, areacode = ""):
	"Identifies everything that looks like a phone #, and then puts them into a list."

	import re

	phone = ""

	for item in phone_re.findall(county):
		item = phone_clean(item, areacode)
		phone = phone + item + ", "

	phone = phone.strip(", ")

	return phone


def phone_clean(phone, areacode = ""):
	"Breaks the phone down into digits; assesses what modifications need to be made to those digits; then puts those digits back together into a (555) 555-5555-formatted phone number."

	import re

	d_re = re.compile("\d")

	deconstructed_phone = " ".join(d_re.findall(phone)).split(" ")

	digits = len(deconstructed_phone)

	if "".join(deconstructed_phone[0:2]) == "18": #A 1-800 number screws up the digit counting, so we take out the 1, clean the phone number, and replace it.
		deconstructed_phone.pop(0)

		phone = phone_clean("".join(deconstructed_phone)).replace("(800) ","1-800-")

		return phone

	if digits < 7 or (digits >7 and digits < 10) or (digits ==7 and not areacode):
		return ""
	elif digits == 7 and areacode:
		phone = areacode + phone
		deconstructed_phone = " ".join(d_re.findall(phone)).split(" ")
	elif digits > 10:
		deconstructed_phone.insert(10, " x ")

	#A phone number of the form XXX-1XX... is not valid.

	if deconstructed_phone[3] == "1":
		return ""

	deconstructed_phone.insert(6, "-")
	deconstructed_phone.insert(3, ") ")
	deconstructed_phone.insert(0, "(")

	phone = "".join(deconstructed_phone)

	return phone


def find_emails(email_re, county):
	"Identifies everything that looks like an email, and then puts them into a list."

	import re

	email = ""

	for item in email_re.findall(county):
		if item not in email: #makes sure we don't duplicate
			email = email + item + ", "

	email = email.strip(", ").lower()

	return email



def website_find(website_re, county):
	"This function finds and cleans website URLs from data. website_clean is run separately because we may sometimes want to run it directly from the scraper."

	import re

	website = ""

	for item in website_re.findall(county):
		item = website_clean(item)
		website = website + item + ", "

	website = website.strip(", ")

	return website


def website_clean(website):
	"This function cleans website URLs."

	website = website.replace("//","+++++")

	if "/" not in website and website:
		website = website + "/"

	website = website.replace("+++++","//")

	if "http://" not in website and website:
		website = "http://" + website

	website = website.lower()

	return website


def maps_fips(city, state, zip_code, fips_names, fips_numbers):
	"This function identifies FIPS values for towns where county data isn't available in the data set."

	import time
	import urllib
	import json

	#To begin with, we define an address for the place and grab it from the Google Maps API. Since this leaves us with a pile of JSON, we load it into a JSON object.

	base_url = "http://maps.google.com/maps/api/geocode/json?sensor=false&address=%s"
	
	address = city + " " + state + " " #+ zip_code

	url = base_url % urllib.quote(address)

	place = urllib.urlopen(url)
	json_place = json.load(place)

	#There's a chance Google doesn't have the place. If so, this informs us.

	if json_place['status'] != "OK":
		print json_place
		print "Egad! %s" % address
		sys.exit()

	#At this point, we're looking for the full name of Administrative Area 2 (County). So we cycle through components of the JSON until we find it.

	json_address = json_place['results'][0]['address_components']
	print address
	print json_address
	for i in range(0,len(json_address)):
		if unicode("administrative_area_level_2") in json_address[i]['types']:
			county_name = json_place['results'][0]['address_components'][i]['long_name'].encode('ascii')
			break
	print [county_name]
	print "++++++++++++++++++"

	#Google gives "St" counties-- St. Clair, St. Jude, etc.--without the period, but the FIPs data has them with the period. This inserts the period if it's needed.

	#We already have a function to match county name to FIPs. Go us!

	fips = fips_find(county_name, fips_names, fips_numbers)

	#Google will shut us off if we query it too quickly, so we have this to slow it down.

	time.sleep(2)

	if not fips:
		print address
		print json_place
		return "", county_name

	return fips, county_name


def make_name(name_line, separator, review, order="", ignore = ""):
	"Takes a string containing the authority name and name and breaks it into the authority name, the first name, and last name."

	official = name_line.strip().partition(separator)

	if order == "reverse":
		official_name = official[2]
		authority_name = official[0].title()
	else:
		official_name = official[0]
		authority_name = official[2].title()

	if ", " in official_name:
		official_name_split = official_name.partition(", ")
		official_name = official_name_split[2] + " " + official_name_split[0]

	authority_name = authority_name.strip(", \r\n")

	first_name, last_name, review = split_name(official_name, review, ignore)

	return first_name, last_name, authority_name, review


def split_name(official_name, review, ignore = ""):
	"This function takes a name, checks for a middle name or prefix (and removes it if necessary), and returns a first name and last name."

	import re

	middle_name_re = re.compile(" [A-Z]\.* ")
	nick_re = re.compile("[\(\"\'].+?[\)\"\'] ")
	prefix_re = re.compile("[MD][rs]*\. ")

	for item in middle_name_re.findall(official_name):
		official_name = official_name.replace(item," ")
	for item in nick_re.findall(official_name):
		official_name = official_name.replace(item," ")
	for item in prefix_re.findall(official_name):
		official_name = official_name.replace(item," ")

	if not ignore:
		official_name = official_name.encode("ascii", "ignore").strip()

	name_split = official_name.partition(" ")

	first_name = name_split[0].title().strip(", \r\n")
	last_name = name_split[2].title().strip(", \r\n")

	if "Hon." in first_name:
		last_fixer = last_name.partition(" ")
		first_name = first_name + " " + last_fixer[0]
		last_name = last_fixer[2]

	if " " in last_name:
		review = review + "a"

	return first_name, last_name, review


def pdf_to_text(data): 
	"Converts a PDF to text, as neatly as can reasonably be hoped. Found from Herb Lainchbury in http://www.herblainchbury.com/2010_05_01_archive.html"
	from pdfminer.pdfinterp import PDFResourceManager, process_pdf 
	from pdfminer.pdfdevice import PDFDevice 
	from pdfminer.converter import TextConverter 
	from pdfminer.layout import LAParams 

	import StringIO 
	fp = StringIO.StringIO() 
	fp.write(data) 
	fp.seek(0) 
	outfp = StringIO.StringIO() 

	rsrcmgr = PDFResourceManager() 
	device = TextConverter(rsrcmgr, outfp, laparams=LAParams()) 
	process_pdf(rsrcmgr, device, fp) 
	device.close() 

	t = outfp.getvalue() 
	outfp.close() 
	fp.close() 
	return t