-- name: get_now$
SELECT NOW() AS now;

-- name: comma_nospace_var^
SELECT :one,:two,:three AS comma;

-- NOTE this does not work with mysql which uses backslash escapes
-- name: escape-quotes$
SELECT 'L''art du rire' AS escaped;

-- name: person-attributes^
SELECT :p.name AS name, :p.age AS age;

-- FIXME this one does not work
-- name: my-escape-quotes$
-- SELECT 'L\'art du rire' AS escaped;

-- name: empty$
SELECT 'hello' WHERE FALSE;

-- name: get-modulo$
-- no-escaped percent modulo operator
SELECT :numerator % :denominator AS modulo;

-- name: square$
select :val::int * :val::int as squared;
