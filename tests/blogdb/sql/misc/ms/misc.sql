-- name: ms_get_now_date_time$
SELECT CONVERT(VARCHAR, CURRENT_TIMESTAMP, 120) AS now;

-- name: empty$
SELECT 'hello' AS message WHERE 0 = 1;

-- name: get-modulo$
-- %-escaped percent modulo operator
SELECT :numerator %% :denominator;

-- name: get-modulo-2$
-- no-escape modulo + cast
SELECT :numerator::INT8 % :denominator::INT8;
