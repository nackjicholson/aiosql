-- name: get-modulo$
-- no-escaped percent modulo operator
SELECT :numerator::INT8 % :denominator::INT8 AS modulo;
