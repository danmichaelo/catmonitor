# CatMonitor

Tool to monitor additions of articles to categories, for use in WikiProjects.

Example: http://no.wikipedia.org/w/index.php?title=Portal:Russland/Nye_artikler

Category members are read from the Wikipedia MySql database, using the replicated copy at Toolserver,
and cached in a local SQLite3 file.

## Installation:

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
````

Setup a virtualenv and install deps: 
<pre>
virtualenv env
. env/bin/activate
pip install git+git://github.com/btongminh/mwclient.git
pip install git+git://github.com/danmichaelo/mwtemplates.git
pip install oursql pyyaml werkzeug Jinja2
</pre>
Finally do <code>cp config.dist.yml config.yml</code> and edit to your preference.
