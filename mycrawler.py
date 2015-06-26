import sys
import urllib
from bs4 import BeautifulSoup
import urllib2
from urlparse import urlparse
import time

import MySQLdb as mdb

#
# --- Prints menu
#
def print_cmds():
                return "    Welcome to the my Web Crawler\n" + \
                       "    What do you want to do?\n" + \
                       "    Enter 1 - add link\n" + \
                       "    Enter 2 - parse links links\n" + \
                       "    Enter q - Quit\n" + \
                       "    crawler:"

#
# --- Check a link to see if it's good or bad or has a description then saves it to the 
# database
#
def check_link(source):


	
	if source is None or source.startswith('#') or source.startswith('mailto:'):
		return
		
	if source.startswith('/'):
		source = 'http://www.lanl.gov' + source
		

	if not source.startswith('http://'):
		return
	
	
	if is_ignore(source):
		return
	
	print "testing link: " + source	
	code = ''
	try:

		connection = urllib2.urlopen(source,'',10)
		code = connection.getcode()
		connection.close()
	except urllib2.HTTPError, e:
		code = e.getcode()
	except Exception, e:
		code = '0'


		
	description = ""
	soup = None
	if code is 200:
		try:
			connection = urllib2.urlopen(source,'',10)
		except urllib2.HTTPError, e:
			code = e.getcode()
		except Exception, e:		
			code = '0'	
		
		if connection is None:
			return
			
		soup = BeautifulSoup(connection.read(),'html5lib')
		description = soup.find(attrs={"name":"description"})

		
	
	con = mdb.connect('127.0.0.1', 'root', '', 'crawler');
	with con:
		cur = con.cursor()
		cur.execute("SELECT id FROM `pages` WHERE statusCode is NULL and `link` LIKE '"+source+"' LIMIT 1")       			
		data = cur.fetchone();

		id='0'
		if data != None and data[0] != None:
			id = data[0]

		if description is None:
			description = 'None'

		
		description = str(description).replace("'", "*")



		try:
			sql = "UPDATE `pages` SET `statusCode` = '"+str(code)+"', `description` = '"+description+"' WHERE `id` = '"+str(id)+"';"
			cur.execute(sql)        
		except Exception, e:
			print e
			quit();
			
		if soup != None:
			for link in soup.find_all('a'):
				add_link_to_table(source,link.get('href'))
		

#
# --- Checks the table if this is a know bad page or url.
#
def is_ignore(link):

	if link is None:
		return


	con = mdb.connect('127.0.0.1', 'root', '', 'crawler');
	cur = con.cursor()	
	
	sql = "SELECT * FROM `ignore` WHERE startsWith is NULL and `url` LIKE '"+link+"'"
	cur.execute(sql)       			
	data = cur.fetchone();
	if not data is None:
		return True

			
	sql = "SELECT *  FROM `ignore` WHERE startsWith is NOT NULL AND instr('"+link+"',url)"
	cur.execute(sql)       			
	data = cur.fetchone();
	if not data is None:
		return True


	return False
			
		

#
# --- This adds a link found to the table to be crawled later.
#                       
def add_link_to_table(source, link):


	if link is None or source is None or link.startswith('#') or link.startswith('mailto:') or link.startswith('http://www.lanl.gov/news/'):
		return
		
	if link.startswith('/'):
		link = 'http://www.lanl.gov' + link
		

	if not link.startswith('http://www.lanl.gov'):
		return
		
	if  ".pdf" in link or ".doc" in link or ".mpg" in link or ".avi" in link or ".zip" in link: 
		return
			
	if is_ignore(link):
		return
	
	con = mdb.connect('127.0.0.1', 'root', '', 'crawler');
	with con:
		cur = con.cursor()
		
		
		cur.execute("SELECT id FROM `pages` WHERE (statusCode = '200' or statusCode is NULL) and `link` LIKE '"+link+"' LIMIT 1")       			
		data = cur.fetchone();
		
		if data is None:
			print 'Added: ' 
			#print "INSERT INTO `pages` (`source`, `link`) VALUES	( '"+str(source)+"', '"+str(link)+"' );"
			cur.execute("INSERT INTO `pages` (`source`, `link`) VALUES	( '"+str(source)+"', '"+str(link)+"' );")        		
			print "Done"


def get_next_link():
	con = mdb.connect('127.0.0.1', 'root', '', 'crawler');
	cur = con.cursor()	
	
	sql = "SELECT link FROM `pages` WHERE `statusCode`IS null"
	cur.execute(sql)       			
	data = cur.fetchone();
	if data != None and data[0] != None:
		return data[0]
	return None


def add_links(source):
	connection = urllib2.urlopen(source,'',10)
	if connection is None:
		return
		
	soup = BeautifulSoup(connection.read(),'html5lib')

	for link in soup.find_all('a'):
			add_link_to_table(source,link.get('href'))
                       
def execute_cmd(c):
                if c == '1':
                    print ("Start")
                    source = "http://www.lanl.gov/collaboration/index.php"
                    check_link(source)
                elif c == '2':
					print ("Start")
					while(True):
						link = get_next_link()
						check_link(link)
                		
                elif c == '3':

					link = get_next_link()
					while(link):
						print 'Running'
						link = get_next_link()
						add_links(link)
                elif c == '4':
                	check_link('http://www.lanl.gov/natlsecurity/threat/index.shtml')
                elif c == 'q':
                    print ("End")

#
# -- Main loop
#
def main():
                while(True):
                    
                    #to start the app we manually add a link to the database
                    #c = raw_input(print_cmds())
                    # we just want to continue parsing pages. 
                    c = '2'
                    
                    execute_cmd(c)
                    break
                    if c == 'q' or c == 'Q':
                        break
                    print('Running');
main()
