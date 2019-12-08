-- https://stackoverflow.com/a/15180124
create function non_null_count(variadic arr anyarray)
returns bigint as
$$
    select count(x) from unnest($1) as x
$$ language SQL immutable;