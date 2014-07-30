# CatMonitor

[CatMonitor](//tools.wmflabs.org/catmonitor/) is a tool to monitor additions of articles to categories, for use with WikiProjects. It updates pages such as this: http://no.wikipedia.org/w/index.php?title=Portal:Russland/Nye_artikler

Category members are read from the Wikipedia MySql database, using the replication at Tool Labs,
and cached in a local SQLite3 file.

## Installation:

Install [Bower](//github.com/bower/bower) components:
```
bower install
```

Run <code>sqlite3 catmonitor.db</code> and 
````
CREATE TABLE articles (
  category TEXT NOT NULL,
  article TEXT NOT NULL,
  date_added DATE NOT NULL, 
  date_created DATE,
  PRIMARY KEY (category,article)
);
CREATE INDEX date_added ON articles(date_added);
CREATE INDEX date_created ON articles(date_created);

CREATE TABLE stats (
  id INTEGER PRIMARY KEY,
  category TEXT NOT NULL,
  ts DATE NOT NULL,
  membercount INTEGER
);
CREATE INDEX category ON stats(category);
CREATE INDEX ts ON stats(ts);
````

Setup a virtualenv and install deps: 
<pre>
virtualenv ENV
. ENV/bin/activate
pip install -r requirements.txt
</pre>
Finally do <code>cp config.dist.json config.json</code> and edit to your preference.
