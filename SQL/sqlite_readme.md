#### source: http://www.newthinktank.com/2013/05/sqlite3-tutorial/
SQLite3 Cheat Sheet

sqlite3 test.db // open sqlite and provide a database name
// Creates a table in the database
// Primary Key automatically generates values that start at 1 and increase by 1
// name is a text field that will hold employee names

create table employees (id integer primary key, name text);


// Check table schema
.schema [table_name]
e.g., 
.schema college


// Check current tables
.table


// Insert some employees
insert into employees (id, name) values(1, 'Max Eisenhardt');
insert into employees (name) values('Pietro Maximoff');
insert into employees (name) values('Wanda Maximoff');
insert into employees (name) values('Mortimer Toynbee');
insert into employees (name) values('Jason Wyngarde');
 
// In column mode, each record is shown on a separate line with the data aligned in columns

// Update fields
UPDATE table
SET column_1 = new_value_1,
    column_2 = new_value_2
WHERE
    search_condition 
ORDER column_or_expression
LIMIT row_count OFFSET offset;


// headers on shows the column names, if off they wouldn't show
.mode column
.headers on
select * from employees; // Show all employees
 
 
// Changes the width of the columns
.width 15 20
 
// Closes the database
.exit

sqlite3 test.db // Reopen database
 
.tables // Displays the tables
 
// Displays every value on its own line
 
.mode line
select * from employees;
 
// Shows the statements used to create the database. You could also provide a table name to see how that single table was made
 
.schema OR .schema employees
 
// You can get a more detailed database view
 
.mode column
.headers on
select type, name, tbl_name, sql from sqlite_master order by type;
 
// Used to show the current settings
 
.show
 
// Set NULL to 'NULL'
 
.nullvalue 'NULL'
.show
 
// Change the prompt for SQLite
 
.prompt 'sqlite3> '
.show
 
// Used to export database into SQL format on the screen
 
.dump
 
// Used to output to a file
 
.output ./Documents/sqlite3Files/employees.sql
.dump
.output stdout // Restores output to the screen
 
// You don't delete a database with any command. You have to delete the file itself
 
// You can delete a table however
 
drop table employees;
 
// You can import the table then with
 
.read ./Documents/sqlite3Files/employees.sql
 
// .mode is used to change the formatting of the output
// OPTIONS FOR MODE : column, csv
// html: html table
// insert: insert commands used
// list: List without commas
// tabs: Tab separated list
 
// How to output a CSV list to a file
.mode csv // You could define the output should be csv
.separator ,  // OR define the separator for the columns
.output ./Documents/sqlite3Files/employees.csv
.separator ,
select * from employees;
.output stdout

 
// How to import a table from CSV file
.mode csv
.import [DB_filename] [table_name]
e.g., 
.import student.csv student


// Output html table
 
.mode html
select * from employees;
.output stdout
 
// line outputs column name and value
 
.mode line
select * from employees;
.output stdout
 
// Items with double quotes
 
.mode tcl
select * from employees;
.output stdout
