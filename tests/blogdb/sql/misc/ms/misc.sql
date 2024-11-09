-- name: get_now_date_time()$
SELECT CONVERT(VARCHAR, CURRENT_TIMESTAMP, 120) AS now;

-- name: empty()$
SELECT 'hello' AS message WHERE 0 = 1;

-- name: get-modulo(numerator, denominator)$
SELECT :numerator % :denominator AS modulo;
