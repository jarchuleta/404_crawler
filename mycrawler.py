#!/usr/bin/env python

# TODO: Parameterize queries as the current script is susceptable to SQL Injections via URL.
# This isn't a huge deal since you're crawling your own network of sites, but should follow
# good coding practics anyway.

import sys
import urllib
from bs4 import BeautifulSoup
import urllib2
from urlparse import urlparse
import time
import MySQLdb as mdb
import logging

logLevel = logging.INFO
crawllog = logging.getLogger("crawler")
crawllog.setLevel(logLevel)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logLevel)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
crawllog.addHandler(ch)

protocol = 'https:'
baseurl = protocol + '//some_baseurl.com'
timeout = 15
mysqlParam = {
    'host': 'localhost',
    'user': 'root',
    'passwd': 'SOME_PASSWORD',
    'db': 'crawler',
    'port': 3306
}

opener = urllib2.build_opener()
opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36')]  # Chrome 58.0.3029.110
# opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36')]                       # Chrome 41.0.2228.0
# opener.addheaders = [('User-Agent', 'Mozilla/5.0')]

#
# --- Prints menu
#
def print_cmds():
    return """Welcome to the my Web Crawler
           What do you want to do?
           Enter 1 - add link
           Enter 2 - parse links links
           Enter q - Quit
           crawler:"""

#
# --- Check a link to see if it's good or bad or has a description then saves it to the
# database
#
def check_link(source):
    if source is None or source.startswith('#') or source.startswith('mailto:'):
        return

    if source.startswith('//'):
        source = protocol + source

    if source.startswith('/'):
        source = baseurl + source

    if not source.startswith(protocol):
        return

    if is_ignore(source):
        return

    crawllog.info("testing link: %s", source)
    code = ''
    try:
        connection = opener.open(source,'',timeout)
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
            connection = opener.open(source,'',timeout)
        except urllib2.HTTPError, e:
            code = e.getcode()
        except Exception, e:
            code = '0'

        if connection is None:
            return

        try:
            soup = BeautifulSoup(connection.read(),'html5lib')
            description = soup.find(attrs={"name":"description"})
        except Exception, e:
            crawllog.error(e)
            return

    con = mdb.connect(**mysqlParam)
    with con:
        cur = con.cursor()
        cur.execute("SELECT id FROM `pages` WHERE statusCode is NULL and `link` LIKE '"+source+"' LIMIT 1")
        data = cur.fetchone()

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
            crawllog.error(e)
            quit()

        if soup != None:
            for link in soup.find_all('a'):
                add_link_to_table(source,link.get('href'))


#
# --- Checks the table if this is a know bad page or url.
#
def is_ignore(link):

    if link is None:
        return

    sql = "SELECT * FROM `ignore` WHERE startsWith is NULL and `url` LIKE '"+link+"'"
    try:
        con = mdb.connect(**mysqlParam)
        cur = con.cursor()
    
        cur.execute(sql)
        data = cur.fetchone()
        if not data is None:
            return True
    
        sql = "SELECT *  FROM `ignore` WHERE startsWith is NOT NULL AND instr('"+link+"',url)"
        cur.execute(sql)
        data = cur.fetchone()
        if not data is None:
            return True
    except Exception as e:
        crawllog.error(e)
        crawllog.error(sql)
        return True  # Posibly bad URL or SQL injection URL, so ignore it.

    return False


#
# --- This adds a link found to the table to be crawled later.
#
def add_link_to_table(source, link):
    if link is None or source is None or link.startswith('#') or link.startswith('mailto:') or link.startswith(baseurl+'/learn/'):
        return

    if link.startswith('//'):
        link = protocol + link

    if link.startswith('/'):
        link = baseurl + link

    if not link.startswith(baseurl):
        return

    if  ".pdf" in link or ".doc" in link or ".mpg" in link or ".avi" in link or ".zip" in link:
        return

    if is_ignore(link):
        return

    con = mdb.connect(**mysqlParam)
    with con:
        cur = con.cursor()


        cur.execute("SELECT id FROM `pages` WHERE (statusCode = '200' or statusCode is NULL) and `link` LIKE '"+link+"' LIMIT 1")
        data = cur.fetchone()

        if data is None:
            crawllog.info('Added: ')
            #crawllog.info("INSERT INTO `pages` (`source`, `link`) VALUES    ( '"+str(source)+"', '"+str(link)+"' )")
            cur.execute("INSERT INTO `pages` (`source`, `link`) VALUES    ( '"+str(source)+"', '"+str(link)+"' );")
            crawllog.info("Done")


def get_next_link():
    con = mdb.connect(**mysqlParam)
    cur = con.cursor()

    sql = "SELECT link FROM `pages` WHERE `statusCode` IS null"
    cur.execute(sql)
    data = cur.fetchone()
    if data != None and data[0] != None:
        return data[0]
    return None


def add_links(source):
    connection = opener.open(source,'',timeout)
    if connection is None:
        return

    try:
        soup = BeautifulSoup(connection.read(),'html5lib')
    except Exception, e:
        crawllog.error(e)
        return

    for link in soup.find_all('a'):
        add_link_to_table(source,link.get('href'))

def execute_cmd(c):
                if c == '1':
                    crawllog.info("Start")
                    source = baseurl
                    check_link(source)
                elif c == '2':
                    crawllog.info("Start")
                    while(True):
                        link = get_next_link()
                        crawllog.debug("Got link: %s", link)
                        check_link(link)
                        crawllog.debug("Checked link: %s", link)

                elif c == '3':
                    link = get_next_link()
                    while(link):
                        crawllog.info('Running')
                        link = get_next_link()
                        add_links(link)
                elif c == 'q':
                    crawllog.info("End")

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
        crawllog.info('Running')

main()
