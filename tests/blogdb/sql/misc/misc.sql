-- name: get_now$
SELECT NOW();

-- name: get_now_date_time$
SELECT strftime('%Y-%m-%d %H:%M:%S', datetime());

-- name: pg_get_now_date_time$
SELECT to_char(NOW(), 'YYYY-MM-DD HH24:MI:SS');

-- name: my_get_now_date_time$
SELECT date_format('%Y-%m-%d %H:%i:%S', NOW());
