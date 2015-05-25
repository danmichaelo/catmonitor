# CatMonitor

[CatMonitor](//tools.wmflabs.org/catmonitor/) is a tool to monitor additions of articles to categories, for use with WikiProjects. It updates pages such as this: http://no.wikipedia.org/w/index.php?title=Portal:Russland/Nye_artikler

Category members are read from the Wikipedia MySql database, using the replication at Tool Labs,
and cached in a local SQLite3 file.

## Installation:

Install [Bower](//github.com/bower/bower) components:
```
bower install
```

Run `./migrations/*.sh` to initialize the MySQL database and create tables.

Setup a virtualenv and install deps: 
<pre>
virtualenv ENV
. ENV/bin/activate
pip install -r requirements.txt
</pre>
Finally do <code>cp config.dist.json config.json</code> and edit to your preference.
