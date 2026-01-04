-- name: get_now()$
SELECT NOW() AS now;

-- name: comma_nospace_var(one, two, three)^
SELECT :one,:two,:three AS comma;

-- NOTE this does not work with mysql which uses backslash escapes
-- name: escape-quotes()$
SELECT 'L''art du rire' AS escaped;

-- name: person-attributes(p)^
SELECT :p.name AS name, :p.age AS age;

-- FIXME this one does not work
-- name: my-escape-quotes()$
-- SELECT 'L\'art du rire' AS escaped;
SELECT 1;

-- name: empty()$
SELECT 'hello' WHERE FALSE;

-- name: get-modulo(numerator, denominator)$
-- no-escaped percent modulo operator
SELECT :numerator % :denominator AS modulo;

-- name: square(val)$
select :val::int * :val::int as squared;

-- name: not_a_select()
INSERT INTO Foo VALUES (1);
