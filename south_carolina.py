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
tmpdir = cdir + "tmp/"

voter_state = "SC"
source = "State"


result = [("authory_name", "first_name", "last_name", "county_name", "fips",
    "street", "city", "address_state", "zip_code",
    "po_street", "po_city", "po_state", "po_zip_code",
    "reg_authority_name", "reg_first", "reg_last",
    "reg_street", "reg_city", "reg_state", "reg_zip_code",
    "reg_po_street", "reg_po_city", "reg_po_state", "reg_po_zip_code",
    "reg_phone", "reg_fax", "reg_email", "reg_website", "reg_hours",
    "phone", "fax", "email", "website", "hours", "voter_state", "source", "review")]

#Every county is on a different webpage so we have to cycle through them all.
#To do so, we go elsewhere, extract a list of counties, then later grab a series of web pages based on that list.
#(Writing it to a file isn't strictly necessary, but saves some time down the line.)

file_path = tmpdir + "south_carolina-counties.html"
url = "http://www.scvotes.org/how_to_register_absentee_voting"
data = urllib.urlopen(url).read()
output = open(file_path,"w")
output.write(data)
output.close()

data = open(file_path).read()

#First, we trim the counties page to the minimum needed information, which starts at the list of per-county links.

data = data.partition("<a href=\"/how_to_register_absentee_voting/abbeville\" class=\"page-next\"")[0]

#For each county, we grab a URL ender (county_links) and the county name, as represented in the URL (county_links_names).

county_link_re = re.compile("(/how_to_register_absentee_voting/.+?)\">")
county_link_name_re = re.compile("/how_to_register_absentee_voting/(.+?)\">")

county_links = county_link_re.findall(data)
county_link_names = county_link_name_re.findall(data)

#Once we have those in place, we start setting up regexes that are used in cleaning individual counties.

county_name_re = re.compile(">([^<>]+? County) .+?<[pbr /]>")
relevant_re = re.compile("(<div class=\"content.+?)<!-- end content", re.DOTALL)

phone_re =re.compile(">[^x]*?(\(*\d{3}\)*[ -]*\d{3}-.+?)[<F]")
phone_format_re = re.compile("(\(*\d{3}\)* *\d{3}-\d{4})")
area_code_re = re.compile("\(\d{3}\) ")
digit_re = re.compile("\d")
fax_re = re.compile("Fax.+?(\(*\d{3}\)*.+?)<")

official_name_1_re = re.compile("Director[</u>]* *[:-] *([A-Za-z\. -]+).+?<")
official_name_2_re = re.compile("<[br /p]*>([A-Za-z\. -]+?)<[^<>]*><[^<>]*>[Email: ]*<a href=\"mailto:")
official_name_3_re = re.compile("<[br /p]*>([A-Za-z\. -]+?)<[^<>]*><[^<>]*><[^<>]*><a href=\"mailto:")
official_name_4_re = re.compile("<[br /p]*>([A-Za-z\. -]+?)<[^<>]*><[^<>]*><[^<>]*><a href=\"/files")
official_name_5_re = re.compile(">([A-Za-z\. -]+?), [^<>]*?Director")
official_name_6_re = re.compile("Fax .+?<[^<>]*><[^<>]*>([A-Za-z\. -]+?)<")


website_re = re.compile("a href=\"(h.+?)\"")
#email_re = re.compile("mailto:%*2*0*(.+?) *\".*?>")
email_re = re.compile("[A-Za-z\.-]+?@[A-Za-z\.-]+")

email_junk_re = re.compile("@[^<>]+?\.[cg]o[mv](.*?)<")

font_re = re.compile("</*font.+?>")
style_re = re.compile("(style.+?\")>")
span_re = re.compile("</*span.+?>")
w_re = re.compile("</*w:.+?>")
u_re = re.compile("</*u>")
m_re = re.compile("</*m:.+?>")
set_re = re.compile("{.+?}")
comment_re = re.compile("<!--.+?>")

charleston_re = re.compile(" [A-Z][A-Z](.+?)\d{5}[\d-]*")
richland_fix_re = re.compile("Military and Overseas Correspondence.+?</a>")

address_re = re.compile("<[br p/]*>([^<>]*\d[^>]+?<.+?\d{5}[\d-]*) *<[brp/ ]*>")
csz_re = re.compile("[\d>] *([A-Za-z \.]+?,* [A-Z][A-Z] +\d{5}[\d-]*)")
po_re = re.compile("(P*o*s*t* *Of*i*c*e* .+?)<")
city_re = re.compile("(.+?),* [A-Z][A-Z] ")
state_re = re.compile(" ([A-Z][A-Z]) ")
zip_re = re.compile("\d{5}[\d-]*")
zip_mod_re = re.compile("\(\d{5}[\d-]*\)")
mailing_region_re = re.compile("Mailing Address.+?[A-Z][A-Z] \d{5}[\d-]* *<[brp/ ]*>")



for link in county_links:

	authority_name, first_name, last_name, county_name, town_name, fips, street, city, address_state, zip_code, po_street, po_city, po_state, po_zip_code, reg_authority_name, reg_first, reg_last, reg_street, reg_city, reg_state, reg_zip_code, reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code, reg_phone, reg_fax, reg_email, reg_website, reg_hours, phone, fax, email, website, hours, review = dogcatcher.begin(voter_state)

	link_name = county_link_names[county_links.index(link)]

	file_name = tmpdir  + link_name + "-sc-clerks.html"
	url = "http://www.scvotes.org" + link

	data = urllib.urlopen(url).read()
	output = open(file_name,"w")
	output.write(data)
	output.close()

	county = open(file_name).read()

	#Trimming the county.
	county = relevant_re.findall(county)[0]

	#There are a tremendous number of useless HTML tags or county-specific fixes. This code cleans them up so we don't have to deal with them elsewhere.

	for junk in email_junk_re.findall(county):
		county = county.replace(junk,"")
	for font in font_re.findall(county):
		county = county.replace(font,"")
	for style in style_re.findall(county):
		county = county.replace(style,"")
	for span in span_re.findall(county):
		county = county.replace(span,"")
	for w in w_re.findall(county):
		county = county.replace(w,"")
	for u in u_re.findall(county):
		county = county.replace(u,"")
	for m in m_re.findall(county):
		county = county.replace(m,"")
	for comment in comment_re.findall(county):
		county = county.replace(comment,"")
	for s in set_re.findall(county):
		county = county.replace(s,"")
	for item in charleston_re.findall(county):
		county = county.replace(item," ")
	for item in richland_fix_re.findall(county):
		county = county.replace(item," ")

	#fixing errors in Dillon, Florence, and Newberry Counties
	county = county.replace("sedwardsvr17","<a href=\"mailto:sedwardsvr17@aol.com\"").replace("%3",":").replace("%40","@").replace("brogers","<a href=\"mailto:brogers@newberrycounty.net\"")

	county_name = county_name_re.findall(county)[0].replace(" County","").strip()

	print "__________________________________"
	#unique case in Aiken County:
	if county_name == "Aiken County":
		reg_email = "cholland@aikencountysc.gov"
		county.replace("cholland@aikencountysc.gov","")



	phone = dogcatcher.find_phone(phone_re, county)
	for item in phone_re.findall(county):
		county = county.replace(item, "")
	#Many of the fax numbers don't have area codes. So we grab the first area code we find in the block of phone numbers and give it to the fax number.
	area_code = area_code_re.findall(phone)[0]
	fax = dogcatcher.find_phone(fax_re, county, area_code)
	for item in fax_re.findall(county):
		county = county.replace(item, "")
	county = county.replace("Fax", "")

	#unique case in Greenwood County, which gives a separate phone number for registration-related contacts:
	if county_name == "Greenwood County":
		phone = "(864) 942-3152, (864) 942-3153, (864) 942-5667"
		fax = "(804) 942-5664"
		county = county.replace(phone,"").replace(fax,"")
		reg_phone = "(864) 942-8585"
		county.replace("(864) 942-8585","")
		reg_fax = "(846) 942-5664"
		county.replace("942-5664","")

	#Some counties have a registration-only email address. In those counties, the absentee email has "absentee" in it.
	#Websites have similar problems

	print county

	email = dogcatcher.find_emails(email_re, county)

	if "absentee" in email:
		emails = email.split(", ")
		email = ""
		for item in emails:
			county = county.replace(item, "")
			if "absentee" in item:
				email = email + ", " + item
			else:
				reg_email = reg_email + ", " + item

		email = email.strip(", ")
		reg_email = reg_email.strip(", ")
	else:
		for item in email_re.findall(county):
			county = county.replace(item, "")

	website = dogcatcher.find_website(website_re, county)

	if "absentee" in website:
		websites = website.split(", ")
		website = ""
		for item in websites:
			county = county.replace(item, "")
			if "absentee" in item:
				website = website + ", " + item
			else:
				reg_website = reg_website + ", " + item
	else:
		for item in website_re.findall(county):
			county = county.replace(item, "")


		website = website.strip(", ")
		reg_website = reg_website.strip(", ")

	print [email]



	#There are many forms the official's name can take. This tries all of them.

	if official_name_1_re.findall(county):
		official_name = official_name_1_re.findall(county)[0].strip()
	elif official_name_2_re.findall(county):
		official_name = official_name_2_re.findall(county)[0].strip()
	elif official_name_3_re.findall(county):
		official_name = official_name_3_re.findall(county)[0].strip()
	elif official_name_4_re.findall(county):
		official_name = official_name_4_re.findall(county)[0].strip()
	elif official_name_5_re.findall(county):
		official_name = official_name_5_re.findall(county)[0].strip()
	elif official_name_6_re.findall(county):
		official_name = official_name_6_re.findall(county)[0].strip()
	else:
		official_name = ""


	if official_name:
		first_name, last_name, review = dogcatcher.split_name(official_name, review)

	county = county.replace(official_name,"")


	print "++++++++++++++++++++++++++++++++++++++"
	if county_name == "Charleston County":
		county = county.replace("Post Office","Mailing Address:<> Post Office")

	#Some counties don't put a marked "Mailing Address" section, but do have a separate mailing address.
	#So first, we check whether the county has "Mailing Address" in it.

	if "Mailing Address" not in county:

		#This section finds the full address. After finding the address, it identifies a city/state/zip (csz) combination and a PO Box number if that exists.
	    #It removes both the CSZ and the PO Address (if it exists) from the full address, leaving behind a street address with some garbage.
    	#It then cleans up the street address and pulls the city, state, and zip out of the csz, and assigns them as appropriate to the street address and state.

		address = address_re.findall(county)[0]
		csz = csz_re.findall(address)[0]
		address = address.replace(csz,"")

		try:
			po_street = po_re.findall(address)[0].replace("</b><p>","")
		except:
			po_street = ""
		street = address.replace(po_street,"").replace(csz,"").replace("</b><p>","")

		street = street.replace("<p>",", ").replace("</p>",", ").replace("<br />",", ").replace(",,",", ").replace(" ,",",").replace(",,",", ").replace(", , ",", ").strip(" /,")

		if po_street:
			po_city = city_re.findall(csz)[0]
			po_state = state_re.findall(csz)[0]
			po_zip_code = zip_re.findall(csz)[0]
		if street:
			city = city_re.findall(csz)[0]
			address_state = state_re.findall(csz)[0]
			zip_code = zip_re.findall(csz)[0]

	else:

		#If there's an explicitly stated mailing address, we find it, and then pull the mailing address out of it.
		#At the same time, we cut the mailing address out of the entire county and find a physical address in what's left of the county.
		#We then clean both of those addresses appropriately.

		mailing_region = mailing_region_re.findall(county)[0]
		county = county.replace(mailing_region,"")
		mailing_addresss = address_re.findall(mailing_region)[0]
		po_street = po_re.findall(mailing_addresss)[0]
		csz = csz_re.findall(mailing_addresss)[0]

		po_city = city_re.findall(csz)[0]
		po_state = state_re.findall(csz)[0]
		po_zip_code = zip_re.findall(csz)[0]

		address = address_re.findall(county)[0]
		csz = csz_re.findall(address)[0]
		street = address.replace(csz,"").replace("</b><p>","")
		street = street.replace("<p>",", ").replace("</p>",", ").replace("<br />",", ").replace(",,",", ").replace(" ,",",").replace(",,",", ").replace(", , ",", ").strip(" /,")
		city = city_re.findall(csz)[0]
		address_state = state_re.findall(csz)[0]
		zip_code = zip_re.findall(csz)[0]

	#Some of the addresses have a more detailed zip code appended to the street address or po_street.
	#This checks for that, reassigns the  and removes it if it appears.

	if zip_mod_re.findall(street):
		zip_code = zip_mod_re.findall(street)[0].strip("()")
		street = street.replace(zip_code,"").strip(" ()")

	if zip_mod_re.findall(po_street):
		po_zip_code = zip_mod_re.findall(po_street)[0].strip("()")
		po_street = po_street.replace(zip_code,"").strip(" ()")

	fips = dogcatcher.find_fips(county_name, voter_state)

	result.append([authority_name, first_name, last_name, county_name, fips,
	street, city, address_state, zip_code,
	po_street, po_city,	po_state, po_zip_code,
	reg_authority_name, reg_first, reg_last,
	reg_street, reg_city, reg_state, reg_zip_code,
	reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code,
	reg_phone, reg_fax, reg_email, reg_website, reg_hours,
	phone, fax, email, website, hours, voter_state, source, review])

#This outputs the results to a separate text file.
dogcatcher.output(result, voter_state, cdir)
