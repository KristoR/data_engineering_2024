## Starting the services

In `compose.yml` we have 1 service:
1) DuckDB
We use a Dockerfile to build the image with DuckDB CLI and Python installation.

Let's start the services:  
`docker compose up -d`

We can then go into the DuckDB service.

`docker exec -it duckdb bash`

## Running DuckDB 

Let's navigate to the subfolder `data`:  
`cd data`

To start DuckDB CLI type `duckdb`

You can now execute SQL queries. For example:
`SELECT 'Hello!' as world;`

You can create a table:  
`CREATE TABLE memory_hello AS SELECT 'Hello!' as world;`

To see the help commands type `.help`

For additional help on a command `.help <command>`


## Creating a persistent database

If you close DuckDB and reopen, then you're no longer able to access the table you created.  
That's because by default, DuckDB works in-memory.  
To persist data, use `.open`.  

Let's create a database `.open practice_session_db`

Recreate the table. By default, it is now on the newly created database.   
`CREATE TABLE memory_hello AS SELECT 'Hello!' as world;`

`.quit` DuckDB and reopen, the table will be accessible if you repeat the steps for opening the database. 

You can also observe that a file has been created in the `data` folder containing the database.

## Working with external files

Let's download some data. Run the following commands (outside of DuckDB):

`curl -L -o userdata1.parquet https://github.com/Teradata/kylo/raw/refs/heads/master/samples/sample-data/parquet/userdata1.parquet`  

`curl -L -o users.json https://jsonplaceholder.typicode.com/users`  

We can query this data directly in DuckDB:  
`SELECT * FROM userdata1.parquet;`  

Alternatively, use the `read_parquet` function:  
`SELECT * FROM read_parquet('userdata1.parquet');`

DuckDB supports dot-notation for nested data, e.g.:   
`SELECT * FROM users.json`

This JSON has several nested fields (struct data type). Try running the following commands:

`SELECT address.street FROM users.json`  

`SELECT * EXCLUDE(geo), geo.* FROM (SELECT address.* FROM users.json);`

## Exporting to files

You can use `.output <filename>` to output everything into a file.  
`.output stdout` to return to default.

If you want to export a single query, you can use `.mode csv` and `.once <file_name>`, for example:  
`.mode csv`  
`.once test.csv`  
`SELECT * EXCLUDE(geo), geo.* FROM (SELECT address.* FROM users.json);`  

The above are CLI specific. You can also use SQL `COPY` statement which works in other clients as well.  
E.g.:   
`COPY (SELECT * FROM users.json) TO output.parquet (FORMAT PARQUET);`

Further info:  
https://duckdb.org/docs/api/cli/overview

For Python client:  
https://duckdb.org/docs/api/python/overview