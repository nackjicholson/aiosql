-- name: get_now_date_time()$
select strftime(now(),'%Y-%m-%d %H:%M:%S') AS now;
