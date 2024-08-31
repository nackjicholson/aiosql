-- name: get_now_date_time$
SELECT date_format(NOW(), '%%Y-%%m-%%d %%H:%%i:%%S') AS now;
