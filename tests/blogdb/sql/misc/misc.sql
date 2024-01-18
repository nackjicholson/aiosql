-- name: get_now$
SELECT NOW();

-- name: get_now_date_time$
SELECT strftime('%Y-%m-%d %H:%M:%S', datetime());

-- name: duckdb_get_now_date_time$
select strftime(now(),'%Y-%m-%d %H:%M:%S');

-- name: pg_get_now_date_time$
SELECT to_char(NOW(), 'YYYY-MM-DD HH24:MI:SS');

-- name: my_get_now_date_time$
SELECT date_format(NOW(), '%Y-%m-%d %H:%i:%S');

-- name: comma_nospace_var^
SELECT :one,:two,:three AS comma;

-- NOTE this does not work with mysql which uses backslash escapes
-- name: escape-quotes$
SELECT 'L''art du rire' AS escaped;

-- name: pg-escape-quotes$
SELECT '''doubled'' single quotes' as """doubled"" double quotes"

-- FIXME this one does not work
-- name: my-escape-quotes$
-- SELECT 'L\'art du rire' AS escaped;

-- name: empty$
SELECT TRUE WHERE FALSE;
