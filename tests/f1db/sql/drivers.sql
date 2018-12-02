-- name: $get-drivers
-- Get drivers dictionaries
select * from drivers;


-- name: get-drivers-born-after
-- Get drivers in order by their age (youngest -> oldest) born
-- who were born after the given date
  select driverref,
         code,
         number,
         dob
    from drivers
   where dob > :dob
order by dob desc;


-- name: get-drivers-by-nationality
-- Get drivers who share the same nationality
  select driverid,
         driverref,
         number,
         code,
         forename,
         surname,
         dob,
         nationality
    from drivers
   where nationality = :nationality;


-- name: create-new-driver<!
-- Make a new entry in the drivers table
insert into drivers (
  driverref,
  number,
  code,
  forename,
  surname,
  dob,
  nationality,
  url
) values (
  :driverref,
  :number,
  :code,
  :forename,
  :surname,
  :dob,
  :nationality,
  :url
);


-- name: create-new-driver-pg<!
-- Make a new driver using postgresql return syntax
insert into drivers (
  driverref,
  number,
  code,
  forename,
  surname,
  dob,
  nationality,
  url
) values (
  :driverref,
  :number,
  :code,
  :forename,
  :surname,
  :dob,
  :nationality,
  :url
)
returning driverid;


-- name: delete-driver!
-- Remove a driver from the database
delete from drivers where driverid = :driverid;
