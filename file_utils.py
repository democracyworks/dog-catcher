import urllib
import urllib2
import os

def base_dir():
  return os.path.dirname(os.path.abspath(__file__)) + "/"

def expand_filename(filename):
  tmpdir = base_dir() + "tmp/"
  return tmpdir + filename

def download_file(filename, url):
  file_path = expand_filename(filename)
  data = urllib.urlopen(url).read()
  output = open(file_path,"w")
  output.write(data)
  output.close()

def read_file_contents(filename):
  return open(expand_filename(filename)).read()
