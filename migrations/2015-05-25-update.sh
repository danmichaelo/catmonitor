#!/bin/bash

USER=s51280

mysql --defaults-file="${HOME}"/replica.my.cnf -h tools-db << END

USE ${USER}__catmonitor ;

ALTER TABLE articles ADD article_path MEDIUMTEXT COLLATE utf8_bin;

END

