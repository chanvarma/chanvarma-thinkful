-- Written by: Chanakya Varma

-- Data Exploration

-- 1. Write a query that allows you to inspect the schema of the naep table.
SELECT 
	table_name, 
	column_name,
	is_nullable,
	data_type,
	is_identity
FROM 
	information_schema.columns
	-- (earlier submission) INFORMATION_SCHEMA.COLUMNS 
WHERE 
	table_name = 'naep';
	
-- 2. Write a query that returns the first 50 records of the naep table.
SELECT *
FROM 
	naep
LIMIT 50;

-- 3. Write a query that returns summary statistics for avg_math_4_score by state. Make sure to sort the results alphabetically by state name.

SELECT
	state,
	COUNT(avg_math_4_score) AS count,
	ROUND(AVG(avg_math_4_score), 3) AS avg_grade4_score,
	ROUND(MIN(avg_math_4_score), 3) AS min_grade4_score,
	ROUND(MAX(avg_math_4_score), 3) AS max_grade4_score
	(earlier submission ROUND(AVG(avg_math_4_score), 3) AS avg_grade4_score,
	-- (earlier submission) ROUND(MIN(avg_math_4_score), 3) AS min_grade4_score,
	-- (earlier submission) ROUND(MAX(avg_math_4_score), 3) AS max_grade4_score
FROM 
	naep
GROUP BY
	state
ORDER BY
	state ASC;
	
	
-- 4. Write a query that alters the previous query so that it returns only the summary statistics for avg_math_4_score by state with differences in max and min values that are greater than 30.

SELECT
	state,
	COUNT(avg_math_4_score) AS count,
	ROUND(AVG(avg_math_4_score), 3) AS avg_grade4_score,
	ROUND(MIN(avg_math_4_score), 3) AS min_grade4_score,
	ROUND(MAX(avg_math_4_score), 3) AS max_grade4_score,
	-- (earlier submission) ROUND(MAX(avg_math_4_score) - MIN(avg_math_4_score), 3) AS range
FROM 
	naep
GROUP BY
	state
HAVING 
	(ROUND(MAX(avg_math_4_score) - MIN(avg_math_4_score), 3)) > 30
ORDER BY
	state ASC;
	
-- Analyzing your data

-- 5. Write a query that returns a field called bottom_10_states that lists the states in the bottom 10 for avg_math_4_score in the year 2000.

SELECT 
	state AS bottom_10_states, avg_math_4_score
FROM 
	naep
WHERE
	year = 2000 AND
	-- (earlier submission) avg_math_4_score IS NOT NULL
ORDER BY 
	avg_math_4_score ASC
LIMIT 10;

-- 6. Write a query that calculates the average avg_math_4_score rounded to the nearest 2 decimal places over all states in the year 2000.

SELECT
	ROUND(AVG(avg_math_4_score), 2) AS 		national_avg_math_4_score_in_2000
FROM 
	naep
WHERE
	year = 2000 AND
	-- (earlier submission) avg_math_4_score IS NOT NULL;
	
-- 7. Write a query that returns a field called below_average_states_y2000 that lists all states with an avg_math_4_score less than the average over all states in the year 2000.

SELECT 
	state AS states_below_national_avg, 
	avg_math_4_score
FROM 
	naep
WHERE
	year = 2000 AND
	avg_math_4_score < (
						SELECT
							ROUND(AVG(avg_math_4_score), 2) 
							FROM 
								naep
							WHERE
								year = 2000 AND
								avg_math_4_score IS NOT NULL
						)	
ORDER BY 
	avg_math_4_score ASC;

-- 8. Write a query that returns a field called scores_missing_y2000 that lists any states with missing values in the avg_math_4_score column of the naep data table for the year 2000.

SELECT
	state AS scores_missing_y2000,
	avg_math_4_score, 
	year
FROM 
	naep
WHERE
	avg_math_4_score IS NULL AND
	year = 2000;
	
-- 9. Write a query that returns for the year 2000 the state, avg_math_4_score, and total_expenditure from the naep table left outer joined with the finance table, using id as the key and ordered by total_expenditure greatest to least. Be sure to round avg_math_4_score to the nearest 2 decimal places, and then filter out NULL avg_math_4_scores in order to see any correlation more clearly.

SELECT 
	naep.state,
	naep.year,
	ROUND(avg_math_4_score, 2) AS avg_math_4_score,
	total_expenditure,
	instruction_expenditure
FROM
	naep LEFT OUTER JOIN finance
ON 
	naep.id = finance.id
WHERE
 	avg_math_4_score IS NOT NULL AND
	total_expenditure IS NOT NULL AND
	naep.year = 2000
ORDER BY
	total_expenditure DESC;


-- Calculating the actual correlation coefficient
SELECT 
	CORR(ROUND(avg_math_4_score, 2), total_expenditure) AS corr_math4score_totalexp,
	CORR(ROUND(avg_math_4_score, 2), instruction_expenditure)AS corr_math4score_instrexp
FROM
	naep LEFT OUTER JOIN finance
ON 
	naep.id = finance.id
WHERE
 	avg_math_4_score IS NOT NULL AND
	total_expenditure IS NOT NULL AND
	naep.year = 2000;




