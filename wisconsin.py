import re
import xlrd
import dogcatcher
from file_utils import *

voter_state = "WI"
source = "State"

po_address_re = re.compile(r'(\d+)\s+PO\sBOX')
missing_number_identifier_re = re.compile(r'\s{2,}\d+\s*\Z')
town_name_full_re = re.compile(r'(.+?)\s-\s')

def format_datum(datum):
  return (str(datum)).strip()

def city_data(county_name, county_fips, town_name, row):
  street, city, address_state, zip_code = "","","",""
  po_street, po_city, po_state, po_zip_code = "","","",""

  po_address = po_address_re.search(row[6])
  if po_address == None:
    if missing_number_identifier_re.search(row[6]):
      s = str(row[6]).strip()
      index = s.rfind("  ")
      street = s[:index].strip() + " # " + s[index:].strip()
    else:
      street = row[6]
    city, address_state, zip_code = row[7],row[8],row[9]
  else:
    # In the data set, po address is listed as "XXX PO BOX", we want
    # to swap that around to "PO BOX XXX"
    po_street = "PO BOX " + po_address.group(1)
    po_city, po_state, po_zip_code = row[7],row[8],row[9]

  town_name_full = town_name_full_re.search(row[1]).group(1)

  data = ['', row[3], row[2], town_name, county_name, county_fips,
          street, city, address_state, zip_code,
          po_street, po_city, po_state, po_zip_code,
          '','','','','','','','',
          '','','','','','','','',
          row[10],'',row[5],'','',voter_state,source,'',town_name_full]
  return map(format_datum, data)

# download html page that lists files so we can find the right file
download_file("wisconsin-file-list.html", "http://gab.wi.gov/clerks/directory")
file_list = read_file_contents("wisconsin-file-list.html")

county_and_clerks_re = re.compile("<a href=\"(.+?)\">WI County and Municipal Clerks")
county_and_clerks_url = county_and_clerks_re.findall(file_list)[0]

# download source xls file
download_file("wisconsin-data.xls", county_and_clerks_url)

workbook = xlrd.open_workbook(expand_filename('wisconsin-data.xls'))
worksheet = workbook.sheet_by_name('Sheet1')

current_county = None
current_fips = None
header_row = ["authority_name", "first_name", "last_name", "town_name",
    "county_name", "fips", "street", "city", "address_state", "zip_code",
    "po_street", "po_city", "po_state", "po_zip_code",
    "reg_authority_name", "reg_first", "reg_last",
    "reg_street", "reg_city", "reg_state", "reg_zip_code",
    "reg_po_street", "reg_po_city", "reg_po_state", "reg_po_zip_code",
    "reg_phone", "reg_fax", "reg_email", "reg_website", "reg_hours",
    "phone", "fax", "email", "website", "hours", "voter_state",
    "source", "review", "town_name_full"]

cities = [header_row]

county_name_re = re.compile(r'(.+?)\sCOUNTY\s')
town_name_re = re.compile(r'^(TOWN|CITY|VILLAGE)\sOF\s(.+?)\s-.*', re.DOTALL)

# process XLS, separate counties from cities
for curr_row in range(1, worksheet.nrows):
  row = worksheet.row_values(curr_row)
  county_name = county_name_re.search(row[1])
  if county_name:
    current_county = county_name.group(1)
    current_fips = dogcatcher.find_fips(current_county, voter_state)
  else:
    town_name = town_name_re.search(row[1])
    if town_name:
      cities.append(city_data(current_county, current_fips, town_name.group(2), row))
    else:
      print "skipping: " + row[1]

dogcatcher.output(cities, voter_state, base_dir(), "cities")
