-- name: get_now$
SELECT NOW() AS now;

-- name: get_now_date_time$
SELECT strftime('%Y-%m-%d %H:%M:%S', datetime()) AS now;

-- name: duckdb_get_now_date_time$
select strftime(now(),'%Y-%m-%d %H:%M:%S') AS now;

-- name: pg_get_now_date_time$
SELECT to_char(NOW(), 'YYYY-MM-DD HH24:MI:SS') AS now;

-- name: my_get_now_date_time$
SELECT date_format(NOW(), '%Y-%m-%d %H:%i:%S') AS now;

-- name: ms_get_now_date_time$
SELECT CONVERT(VARCHAR, CURRENT_TIMESTAMP, 120) AS now;

-- name: comma_nospace_var^
SELECT :one,:two,:three AS comma;

-- NOTE this does not work with mysql which uses backslash escapes
-- name: escape-quotes$
SELECT 'L''art du rire' AS escaped;

-- name: pg-escape-quotes$
SELECT '''doubled'' single quotes' as """doubled"" double quotes"

-- name: person-attributes^
SELECT :p.name AS nom, :p.age AS age;

-- FIXME this one does not work
-- name: my-escape-quotes$
-- SELECT 'L\'art du rire' AS escaped;

-- NOTE MS SQL Server does not have booleans, hence 0 = 1
-- name: empty$
SELECT 'hello' AS message WHERE 0 = 1;
