-- https://stackoverflow.com/a/15180124
create function non_null_count(variadic p_array arr)
returns bigint as
$$
    select count(x) from unnest($1) as x
$$ language SQL immutable;