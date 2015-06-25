
# 404 crawler
A web crawler written in python. The purpose is to find bad links (404,403, ect) it's also to find pages missing the meta data field.

1. This will crawl a website and parse out links to store in a database.
2. It will follow those links and find more links to crawl.

##Requirements
* Python 2.7.6
* mysql python driver (used MySQL-python-1.2.3) 
* mysql server (used MySQL 5.6.22)
* [beautifulesoup](http://www.crummy.com/software/BeautifulSoup/)
* html parser (used html5lib)

 
##Database
see database.sql for schema
**Pages Table**
contains links crawled and status checked
**Ignore Table**
add special case pages that crash program

----------
