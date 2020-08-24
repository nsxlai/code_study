source: https://towardsdatascience.com/top-sql-interview-questions-you-should-know-in-2020-32ae491e01dd

Top SQL Interview Questions You Should Know in 2020
Questions you should know if you are preparing for any data-related job
Terence S
Terence S
Follow
Apr 1 · 5 min read





Image for post
Image by Gerd Altmann from Pixabay
Most data-related jobs require you to know SQL and you shouldn’t let SQL interview questions be the reason that you don’t get a job. Especially when it comes to querying, it’s pretty quick to learn and you should make sure that you’re ready for some of the most common SQL-related interview questions.
With that, I give you a list of SQL-related interview questions and answers. Enjoy!
Note: If you have no idea how to query in SQL you can learn SQL in five minutes here.
What is SQL?
SQL stands for Structured Query Language. According to Wikipedia, SQL is a domain-specific language used in programming and designed for managing data held in a relational database management system, or for stream processing in a relational data stream management system [1].
What is a Primary Key?
A Primary key is a column (or a set of columns) that uniquely identifies each row in the table. Typically, an ID column is created for this purpose.
What is a clause?
A SQL clause is a well-defined part of a SQL statement that is typically used to filter a result based on pre-defined conditions but is not always the case. For example, ORDER BY is a clause but doesn’t filter a result.
The five main Clauses are the TOP clause, the WHERE clause, the ORDER BY clause, the GROUP BY clause, and the HAVING clause.
What is the difference between the WHERE and HAVING clause?
Both WHERE and HAVING are used to filter a table to meet the conditions that you set. The difference between the two is shown when they are used in conjunction with the GROUP BY clause. The WHERE clause is used to filter rows before grouping (before the GROUP BY clause) and HAVING is used to filter rows after grouping.
What are the different types of joins and explain them each?
Image for post
Image from SQL-Join
There are four different types of joins:
Inner join: Returns records that have matching values in both tables
Left join: Returns all records from the left table and the matched records from the right table
Right join: Returns all records from the right table and the matched records from the left table
Full join: Returns all records when there is a match in either left or right table
What is the difference between a UNION and JOIN?
Both are used to combine data from one or more tables into a single result. The difference is that JOIN statements combine columns of different tables into one result, while UNION statements combine rows of different tables into one result.
What is the difference between DELETE and TRUNCATE statements?
DELETE is used to remove one or more rows from a table. You can rollback data after using the delete statement.
TRUNCATE is used to delete all rows from a table and the data cannot be rolled back after it is performed.
What is a View?
A view is also a table — it is a stored result set of a query on another table or multiple tables, which users can query from like any other table.
What is a Subquery and what are the two types?
A subquery (also called an inner query or a nested query) is a query within another SQL query and is used to return data that will be used in the main query as a condition to further restrict the data to be retrieved [2].
There are two types of subqueries:
Correlated subquery: A correlated subquery cannot be evaluated independently of the outer query because the subquery uses the values of the parent statement.
Uncorrelated subquery: A non-correlated subquery can be considered as an independent query and the output of subquery is substituted in the main query.
You can learn more about them here.
What’s the difference between aggregate and scalar functions? Give some examples for each
An aggregate function performs operations on multiple values to return a single value. Aggregate functions are often used with the GROUP BY and HAVING clauses. Some examples of aggregate functions include the following:
AVG() — Calculates the mean of a collection of values.
COUNT() — Counts the total number of records in a specific table or view.
MIN() — Calculates the minimum of a collection of values.
MAX() — Calculates the maximum of a collection of values.
SUM() — Calculates the sum of a collection of values.
FIRST() — Fetches the first element in a collection of values.
LAST() — Fetches the last element in a collection of values.
A scalar function returns a single value based on the input value. Some examples of scalar functions include the following:
LEN() — Calculates the total length of the given field (column).
UCASE() — Converts a collection of string values to uppercase characters.
LCASE() — Converts a collection of string values to lowercase characters.
CONCAT() — Concatenates two or more strings.
ROUND() — Calculates the round off integer value for a numeric field (or decimal point values).
What is the difference between SQL and MySQL?
To reiterate, SQL is a domain-specific language managing, retrieving, and manipulating structured databases. MySQL is a relational database management system, like Oracle.
TLDR: SQL is a language and MySQL is a database.