#!/bin/bash

for SITE in no nn; do

echo ${SITE}

mysql --defaults-file="${HOME}"/replica.my.cnf -h tools-db << END

DROP DATABASE IF EXISTS s51280__cmon_${SITE} ;
CREATE DATABASE s51280__cmon_${SITE} ;
USE s51280__cmon_${SITE} ;

CREATE TABLE articles (
  category varchar(150) NOT NULL,
  article varchar(180) NOT NULL,
  date_added DATE NOT NULL, 
  date_created DATE,
  PRIMARY KEY (category, article),
  KEY date_added (date_added),
  KEY date_created (date_created)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

CREATE TABLE stats (
  id int(12) PRIMARY KEY,
  category varchar(255) NOT NULL,
  ts DATE NOT NULL,
  membercount int(8),
  KEY category (category),
  KEY ts (ts)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

END

done

