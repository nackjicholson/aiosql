-- name: create-foo!
CREATE TABLE Foo(pk INT PRIMARY KEY, val TEXT NOT NULL);

-- name: drop-foo!
DROP TABLE IF EXISTS Foo;

-- name: count-foo
SELECT COUNT(*) FROM Foo;

-- name: insert-foo!
INSERT INTO Foo(pk, val) VALUES (:pk, :val);

-- name: select-foo-pk
SELECT val FROM Foo WHERE pk = :pk;

-- name: select-foo-all
SELECT pk, val FROM Foo ORDER BY 1;

-- name: update-foo-pk!
UPDATE Foo SET val = :val WHERE pk = :pk;

-- name: delete-foo-pk!
DELETE FROM Foo WHERE pk = :pk;

-- name: delete-foo-all!
DELETE FROM Foo WHERE TRUE;
