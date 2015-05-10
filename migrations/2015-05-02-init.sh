#!/bin/bash

USER=s51280

mysql --defaults-file="${HOME}"/replica.my.cnf -h tools-db << END

DROP DATABASE IF EXISTS ${USER}__catmonitor ;
CREATE DATABASE ${USER}__catmonitor ;
USE ${USER}__catmonitor ;

CREATE TABLE articles (
  category varchar(100) NOT NULL,
  article_id int(11) unsigned NOT NULL,
  article_title varchar(255) NOT NULL,
  wiki varchar(6) NOT NULL,
  date_added DATE NOT NULL, 
  date_created DATE,
  PRIMARY KEY (wiki, category, article_id),
  KEY date_added (date_added),
  KEY date_created (date_created)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 DEFAULT COLLATE=utf8_bin ;

CREATE TABLE stats (
  id int(12) PRIMARY KEY AUTO_INCREMENT,
  category varchar(100) NOT NULL,
  wiki varchar(6) NOT NULL,
  ts DATETIME NOT NULL,
  membercount int(8),
  KEY wc (wiki, category),
  KEY ts (ts)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 DEFAULT COLLATE=utf8_bin ;

END

