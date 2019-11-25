create table survey (
    id serial primary key,
    surveyor varchar(50) not null,
    internal_survey boolean
);

create type osm_type as enum ('node', 'way', 'relation'); 

create table osm_element (
    id serial primary key,
    osm_id integer not null,
    osm_type osm_type not null,
    osm_version integer not null
);

create table data_source (
    id serial primary key,
    osm integer references osm_element(id),
    survey integer references survey(id),
    import_date timestamp,
    constraint one_data_source check (
        non_null_count(osm, survey) = 1
    )
);

create table address (
    id serial primary key,
    free varchar(200),
    locality varchar(100) not null,
    region varchar(100) not null,
    postcode varchar(20),
    country char(2) not null
);

create table building (
    id serial primary key,
    geometry geography(POLYGON),
    address integer references address(id),
    data_source integer not null references data_source(id)
);


create table room (
    id serial primary key,
    name varchar(100),
    level integer not null,
    level_postfix varchar(20),
    ref varchar(20),
    geometry geography(POLYGON),
    data_source integer not null references data_source(id)
);