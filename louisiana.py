import mechanize
import re
import sys
import urllib
import HTMLParser
h = HTMLParser.HTMLParser()
voter_state = "LA"
source = "State"

#cleaning FIPS for use

fips_all = open("C:\Users\pkoms\Documents\TurboVote\Scraping\\fips.txt").read()

fips_data_re = re.compile(".+?LA.+?\n")
fips_number_re = re.compile("\d+")
fips_names_re = re.compile("(.+?)\t")

fips_data = fips_data_re.findall(fips_all)

fips_numbers = []
fips_names = []

for fip in fips_data:
	fips_numbers.append(fips_number_re.findall(fip)[0])
	fips_names.append(fips_names_re.findall(fip)[0])

result = [("authority_name", "first_name", "last_name", "parish_name", "fips",
    "street", "city", "address_state", "zip_code",
    "po_street", "po_city", "po_state", "po_zip_code",
    "reg_authority_name", "reg_first", "reg_last",
    "reg_street", "reg_city", "reg_state", "reg_zip_code",
    "reg_po_street", "reg_po_city", "reg_po_state", "reg_po_zip_code",
    "reg_phone", "reg_fax", "reg_email", "reg_website", "reg_hours",
    "phone", "fax", "email", "website", "hours", "voter_state", "source", "review")]

file_path = "C:\Users\pkoms\Documents\TurboVote\Scraping\louisiana-clerks.html"

# url = "https://voterportal.sos.la.gov/registration/registrarframed.aspx"

# br = mechanize.Browser()
# br.set_handle_robots(False) # ignore robots
# content = br.open(url).read()
# output = open(file_path,"w")
# output.write(content)
# output.close()

data = open(file_path).read()

print data

county_data_re = re.compile("div class=.regList.+?<hr class=.regList", re.DOTALL)
county_name_re = re.compile(">([^>]+?) Parish")

county_data = county_data_re.findall(data)

for county in county_data:
	print "++++++++++++++++++++++++++++++++"
	# print county
	print "--------------------------------"

	county_name_all = county_name_re.findall(county)
	if county_name_all:
		county_name = county_name_all[0]
	else:
		i = 1
		while not county_name:
			county_name_all = county_name_re.findall(county_data[county_data.index(county)-i])
			if county_name_all:
				county_name = county_name_all[0]
			i = i + 1

	print county_name