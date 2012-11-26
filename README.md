Tool to monitor additions of articles to categories, for use in WikiProjects.

Example: http://no.wikipedia.org/w/index.php?title=Portal:Russland/Nye_artikler

Category members are read from the Wikipedia MySql database, using the replicated copy at Toolserver,
and cached in a local SQLite3 file.

To get started, run <code>sqlite3 catmonitor.db</code> and 
````
CREATE TABLE articles (
  category TEXT NOT NULL,
  article TEXT NOT NULL,
  date_added DATE NOT NULL,
  PRIMARY KEY (category,article)
);
````

