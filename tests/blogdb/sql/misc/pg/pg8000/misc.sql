-- name: get-modulo(numerator, denominator)$
-- no-escaped percent modulo operator
SELECT :numerator::INT8 % :denominator::INT8 AS modulo;

-- name: plus(i, j)$
-- line comment with quote
SELECT :i::INT8  -- oops '
     + :j::INT8 AS total -- la '
;
