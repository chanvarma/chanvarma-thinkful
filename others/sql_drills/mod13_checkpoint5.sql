-- Draw a schema of the relationship between the people, salaries, and hof_inducted tables. There are several online database schema drawers that you can use for free, including draw.io, which we recommend. We discuss the basics of how to use draw.io at the end of this checkpoint.
-- Label the primary and foreign keys. (Note that a field can be a primary key to one table and a foreign key to another.)
-- What are the parent and child tables? Are these one-to-one, one-to-many, or many-to-many relationships?

-- ERD: https://imgur.com/gallery/DNv9uAb
-- All the relationships are one-to-one.

-- Write a query that returns the namefirst and namelast fields of the people table, along with the inducted field from the hof_inducted table. All rows from the people table should be returned, and NULL values for the fields from hof_inducted should be returned when there is no match found.

SELECT namelast, namefirst, inducted
FROM people LEFT OUTER JOIN hof_inducted
ON people.playerid = hof_inducted.playerid
ORDER BY namelast ASC;

-- In 2006, a special Baseball Hall of Fame induction was conducted for players from the negro baseball leagues of the 20th century. In that induction, 17 players were posthumously inducted into the Baseball Hall of Fame. Write a query that returns the first and last names, birth and death dates, and birth countries for these players. Note that the year of induction was 2006, and the value for votedby will be “Negro League.”

SELECT namelast, namefirst, birthyear, deathyear, birthcountry inducted
FROM people INNER JOIN hof_inducted
ON people.playerid = hof_inducted.playerid
WHERE yearid = 2006 AND votedby = 'Negro League'
ORDER BY namelast ASC;

-- Write a query that returns the yearid, playerid, teamid, and salary fields from the salaries table, along with the category field from the hof_inducted table. Keep only the records that are in both salaries and hof_inducted. Hint: While a field named yearid is found in both tables, don’t JOIN by it. You must, however, explicitly name which field to include.

SELECT salaries.yearid, salaries.playerid, teamid, salary, category
FROM salaries INNER JOIN hof_inducted
ON salaries.playerid = hof_inducted.playerid
ORDER BY salary DESC;

-- Write a query that returns the playerid, yearid, teamid, lgid, and salary fields from the salaries table and the inducted field from the hof_inducted table. Keep all records from both tables.

SELECT salaries.playerid, salaries.yearid, teamid, lgid, salary, inducted
FROM salaries LEFT OUTER JOIN hof_inducted
ON salaries.playerid = hof_inducted.playerid
ORDER BY salary DESC;

-- There are 2 tables, hof_inducted and hof_not_inducted, indicating successful and unsuccessful inductions into the Baseball Hall of Fame, respectively.
-- Combine these 2 tables by all fields. Keep all records.
-- Get a distinct list of all player IDs for players who have been put up for HOF induction.

SELECT * FROM hof_inducted UNION 
SELECT * FROM hof_not_inducted;












