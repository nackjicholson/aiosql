-- name: get_now_date_time()$
SELECT to_char(NOW(), 'YYYY-MM-DD HH24:MI:SS') AS now;

-- name: escape-simple-quotes()$
SELECT '''doubled'' single quotes' as """doubled"" double quotes"

-- name: get-modulo(numerator, denominator)$
-- %-escaped percent modulo operator
SELECT :numerator %% :denominator AS modulo;
