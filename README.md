
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
** You'll need to upgrade Python's six package to >=1.9.0 for html5lib to work.
*** On Mac, you need to bypass the System version as follows because *pip* won't:

```bash
wget https://pypi.python.org/packages/b3/b2/238e2590826bfdd113244a40d9d3eb26918bd798fc187e2360a8367068db/six-1.10.0.tar.gz#md5=34eed507548117b2ab523ab14b2f8b55
tar -xzf six-1.10.0.tar.gz
cd six-1.10.0
python setup.py install
```
 
##Database
see database.sql for schema
**Pages Table**
contains links crawled and status checked
**Ignore Table**
add special case pages that crash program


## Starting the Application
* Load your database

```bash
mysql -u <user> -p < database.sql
```

* Seed the database with the first URL by running this code.

```sql
    INSERT INTO `pages` (`source`, `link`) 
    VALUES ( 'http://www.lanl.gov/collaboration/index.php', 'http://www.lanl.gov/about/index.php' );
```

* Edit *mycrawler.py* and set the following config:

```python
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
#.
#.
#.
opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36')]  # Chrome 58.0.3029.110
```

* Run the crawler

```bash
python mycrawler.py
```
