DROP TABLE IF EXISTS urls;
DROP TABLE IF EXISTS urlVisits;

SET TIMEZONE TO 'EST';

CREATE TABLE urls (
    original varchar(512),
    scrambled varchar(256),
    ipv4 varchar(15),
    cookieid varchar (36),
);

CREATE TABLE urlVisits (
    scrambled varchar(256),
    ipv4 varchar(15),
    visited TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);