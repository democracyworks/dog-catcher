# -*- coding: latin-1 -*-

def pdf_to_text(data): 
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

def optional_download(file, url):
	from os.path import isfile

	if isfile(file):
		return False

	user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
	headers = {'User-Agent' : user_agent}

	req = urllib2.Request(url, "", headers)
	pdf = urllib2.urlopen(req_abs).read()

	output = open(file, "w")
	output.write(pdf)
	output.close
	return True

def optional_pdf_extract(in_file, out_file):
	if os.path.isfile(out_file):
		return False

	pdf = open(in_file).read()
	data = pdf_to_text(pdf)
	output = open(out_file, "w")
	output.write(data)
	output.close()
	return False

#result.append([first_name, last_name, county_name, 
#	street, city, address_state, zip_code,
#	po_street, po_city,	po_state, po_zip_code,
#	reg_street, reg_city, reg_state, reg_zip_code,
#	reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code,
#	phone, fax, email, website, hours, voter_state, source, review])

import urllib
import re
import sys
import xlrd
import pdfminer
import urllib2
import os

cdir = os.path.dirname(os.path.abspath(__file__))

fips_all = open(os.path.join(cdir, "fips.txt")).read()

fips_data_re = re.compile(".+?IN.+?\n")
fips_number_re = re.compile("\d+")
fips_names_re = re.compile("(.+?)\t")

fips_data = fips_data_re.findall(fips_all)

fips_numbers = []
fips_names = []

for fip in fips_data:
    fips_numbers.append(fips_number_re.findall(fip)[0])
    fips_names.append(fips_names_re.findall(fip)[0])


voter_state = "IN"
source = "State"

result = [("authority_name", "first_name", "last_name", "county_name", "fips",
    "street", "city", "address_state", "zip_code",
    "po_street", "po_city", "po_state", "po_zip_code",
    "reg_authority_name", "reg_first", "reg_last",
    "reg_street", "reg_city", "reg_state", "reg_zip_code",
    "reg_po_street", "reg_po_city", "reg_po_state", "reg_po_zip_code",
    "reg_phone", "reg_fax", "reg_email", "reg_website", "reg_hours",
    "phone", "fax", "email", "website", "hours", "voter_state", "source", "review")]

file_path_abs = os.path.join(cdir, "indiana_absentee.pdf")
file_path_abs_rev = os.path.join(cdir, "indiana_absentee_rev.pdf")
# Technically the third / is incorrect (but harmless) on systems other than Win32
url_abs = "file:///" + file_path_abs

file_path_reg = os.path.join(cdir, "indiana_reg.pdf")
file_path_reg_rev = os.path.join(cdir, "indiana_reg_rev.pdf")
# Technically the third / is incorrect (but harmless) on systems other than Win32
url_reg = "file:///" + file_path_reg

# optional_download(file_path_abs, url_abs)
# optional_download(file_path_reg, url_reg)
# optional_pdf_extract(file_path_abs, file_path_abs_rev)
# optional_pdf_extract(file_path_reg, file_path_reg_rev)

abs_data = open(file_path_abs_rev).read()
reg_data = open(file_path_reg_rev).read()

w_vowel_re = re.compile("[WM] [aeiou]")
elect_re = re.compile("INDIANA ELECTION DIVISION.+", re.DOTALL)
zip_fix_re = re.compile("\d{5}( .+? )\d{4}")
first_re = re.compile(".+?(?=\nSTARKE)", re.DOTALL)

county_data_re = re.compile("\n([A-Z \.]{3,40}.+?\(\d{3}\)[^\n]+)", re.DOTALL)
authority_name_re = re.compile("[^\d].+?[a-z][^\d\n]+")
county_name_re = re.compile("[A-Z \.]+")

address_re = re.compile("\n(P\.*O\.* [BD].+?\d{5}[\d-]* *\n)", re.DOTALL)
address_re_2 = re.compile("\n([^\d\n]*\d.+?\d{5}[\d-]* *\n)", re.DOTALL)
csz_re = re.compile(" *([^,\n]+?, *[A-Z]{2} *\d{5}[\d-]*)")
city_re = re.compile("(.+?),")
state_re = re.compile(" ([A-Z][A-Z]) ")
zip_re = re.compile(" (\d{5}[\d-]*)")
po_re = re.compile("P\.* *O\.* *.+")
phone_re = re.compile("\(\d{3}\)[^\n]+")

for item in elect_re.findall(abs_data):
    abs_data = abs_data.replace(item,"")
for item in w_vowel_re.findall(abs_data):
    abs_data = abs_data.replace(item,item.replace(" ",""))
for item in w_vowel_re.findall(reg_data):
    reg_data = abs_data.replace(item,item.replace(" ",""))
for item in first_re.findall(abs_data):
    abs_data = abs_data.replace(item,"")

for item in zip_fix_re.findall(abs_data):
    abs_data = abs_data.replace(item,item.replace(item,"-"))
for item in zip_fix_re.findall(reg_data):
    reg_data = reg_data.replace(item,item.replace(item,"-"))


abs_counties = county_data_re.findall(abs_data)
reg_counties = county_data_re.findall(reg_data)

print len(abs_counties)
print len(reg_counties)

for county in abs_counties:
    reg_street = ""
    reg_city = ""
    reg_state = "IN"
    reg_zip_code = ""
    reg_po_street = ""
    reg_po_city = ""
    reg_po_state = ""
    reg_po_zip_code = ""
    street = ""
    city = ""
    po_street = ""
    address_state = "IN"
    zip_code = ""
    po_city = ""
    po_state = ""
    po_zip_code = ""
    review = ""
    reg_phone = ""

    county_name = county_name_re.findall(county)[0].strip().title()

    reg_county = ""

    for item in reg_counties:
        reg_county_name_check = county_name_re.findall(item)[0].title().strip()
        if reg_county_name_check in county_name:
            reg_county = item
            reg_county_name = reg_county_name_check
            break
        
    # print "+++++++++++++++++++++++++++++"
    # print [county]
    # print "-----------------------------"

    if county != reg_county:
        print [county]
        print [reg_county]

    # print [reg_county]

    address_try = address_re.findall(county)
    if not address_try:
        address = address_re_2.findall(county)[0]
    else:
        address = address_try[0]
    csz = csz_re.findall(address)[0]

    if not address.replace(csz,""):
        address = po_re.findall(town)[0]

    try:
        po_street = po_re.findall(address)[0].replace(csz,"").strip(", \n")
    except:
        po_street = ""


    street = address.replace(po_street,"").replace(csz,"")
    street = street.replace("\n",", ").replace(" ,",",").strip(" \n/,")


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

    phone = " ".join(phone_re.findall(county)[0].replace("ext"," x ").replace(".","").replace(",","").split())


    reg_address_try = address_re.findall(reg_county)
    if not reg_address_try:
        reg_address = address_re_2.findall(reg_county)[0]
    else:
        reg_address = reg_address_try[0]
    reg_csz = csz_re.findall(reg_address)[0]

    if not reg_address.replace(reg_csz,""):
        reg_address = po_re.findall(town)[0]

    try:
        reg_po_street = po_re.findall(reg_address)[0].replace(reg_csz,"").strip(", \n")
    except:
        reg_po_street = ""


    reg_street = reg_address.replace(reg_po_street,"").replace(reg_csz,"")
    reg_street = street.replace("\n",", ").replace(" ,",",").strip(" \n/,")

    if po_street:
        if street:
            reg_city = city_re.findall(reg_csz)[0]
            reg_address_state = state_re.findall(reg_csz)[0]
            reg_zip_code = zip_re.findall(reg_csz)[0]
        reg_po_city = city_re.findall(reg_csz)[0].strip()
        reg_po_state = state_re.findall(reg_csz)[0].strip()
        reg_po_zip_code = zip_re.findall(reg_csz)[0].strip()
    else:
        reg_city = city_re.findall(reg_csz)[0].strip()
        reg_reg_address_state = state_re.findall(reg_csz)[0].strip()
        reg_zip_code = zip_re.findall(reg_csz)[0].strip()

    reg_phone = " ".join(phone_re.findall(reg_county)[0].replace("ext."," x ").replace(".","").replace(",","").split())

    first_name = ""
    last_name = ""
    website = ""
    email = ""
    fax = ""
    hours = ""
    
    reg_first = ""
    reg_last = ""
    reg_fax = ""
    reg_email = ""
    reg_website = ""
    reg_hours = ""
    fips = ""

    if county_name == "Dekalb":
        county_name = "DeKalb"
    if county_name == "Lagrange":
        county_name = "LaGrange"
    if county_name == "Laporte":
        county_name = "LaPorte"

    authority_name = authority_name_re.findall(county)[0].replace(county_name,"").replace("Co.","").strip()
    reg_authority_name = authority_name_re.findall(reg_county)[0].replace(county_name,"").replace("Co.","").strip()

    fips = dogcatcher.fips_find(county_name, voter_state)

    result.append([authority_name, first_name, last_name, county_name, fips,
    street, city, address_state, zip_code,
    po_street, po_city, po_state, po_zip_code,
    reg_authority_name, reg_first, reg_last,
    reg_street, reg_city, reg_state, reg_zip_code,
    reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code,
    reg_phone, reg_fax, reg_email, reg_website, reg_hours,
    phone, fax, email, website, hours, voter_state, source, review])

output = open("C:\Users\pkoms\Documents\TurboVote\Scraping\indiana.txt", "w")
for r in result:
    output.write("\t".join(r))
    output.write("\n")
output.close()

print len(result)