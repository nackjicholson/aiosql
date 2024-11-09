-- name: get_now_date_time()$
SELECT strftime('%Y-%m-%d %H:%M:%S', datetime()) AS now;
