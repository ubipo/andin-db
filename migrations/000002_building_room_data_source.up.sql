create function non_empty(txt text)
returns boolean as 'select trim($1) <> '''';'
LANGUAGE SQL
IMMUTABLE;

create table import (
    id serial primary key,
    uid uuid not null unique DEFAULT gen_random_uuid(),
    date timestamp not null,
    script varchar(6) not null CHECK (non_empty(script))
);

create table survey (
    id serial primary key,
    uid uuid not null unique DEFAULT gen_random_uuid(),
    surveyor varchar(50) not null CHECK (non_empty(surveyor)),
    external boolean not null
);

create type osm_type as enum ('node', 'way', 'relation'); 

create table osm_element (
    id serial primary key,
    uid uuid not null unique DEFAULT gen_random_uuid(),
    osm_id integer not null,
    osm_type osm_type not null,
    osm_version integer not null
);

create table data_source (
    id serial primary key,
    osm integer references osm_element(id) UNIQUE,
    survey integer references survey(id) UNIQUE,
    import integer not null REFERENCES import(id),
    constraint one_data_source check (
        non_null_count(osm, survey) = 1
    )
);

create table address (
    id serial primary key,
    free varchar(200) CHECK (non_empty(free)),
    locality varchar(100) not null CHECK (non_empty(locality)),
    region varchar(100) not null CHECK (non_empty(region)),
    postcode varchar(20) CHECK (non_empty(postcode)),
    country char(2) not null CHECK (country SIMILAR TO '[a-zA-Z]{2}')
);

create table building (
    id serial primary key,
    uid uuid not null unique DEFAULT gen_random_uuid(),
    name varchar(100) CHECK (non_empty(name)),
    geometry geography(POLYGON) not null,
    address integer references address(id) UNIQUE,
    data_source integer not null references data_source(id)
);

create table room (
    id serial primary key,
    uid uuid not null unique DEFAULT gen_random_uuid(),
    name varchar(100) CHECK (non_empty(name)),
    level integer not null,
    level_postfix varchar(20) CHECK (non_empty(level_postfix)),
    ref varchar(20) CHECK (non_empty(ref)),
    geometry geography(POLYGON) not null,
    building integer not null references building(id),
    data_source integer not null references data_source(id)
);
