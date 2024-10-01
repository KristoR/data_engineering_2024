## Starting the services

In `compose.yml` we have 3 services:
1) dbt  
dbt stores its Docker images on Github. Since we will be connecting to Postgres, we need the version with the Postgres connector.  
2) postgres
we use a Dockerfile to prepopulate our database with some example data
3) pgAdmin
not mandatory, but we can use this as an IDE for accessing Postgres

Let's start the services:  
`docker compose up -d`

We can then go into the dbt service.

`docker exec -it dbt bash`

## Starting a dbt project

We first need to initialize a dbt project. Let's create a project titled "dbt_practice".  

`dbt init dbt_practice`

You will be prompted to choose the database. If you are following this tutorial, you probably only have the Postgres connector, so type 1.

Fill in the rest of the settings based on the `compose.yml` file. You can use `dbname: postgres` and `schema: public`.

The project will now be created and you can see the project files also from your local machine file structure.

The project setup is defined in `dbt_project.yml` file. Some example models have been created as well.

## Creating a dbt profile

The connection to our data warehouse is stored as a dbt profile under `.dbt/profiles.yml`.

Information about profiles can be found here:
https://docs.getdbt.com/docs/core/connect-data-platform/profiles.yml 

dbt will search for profiles in `/root/.dbt/profiles.yml` file - so let's modify this file with the connection details for connecting to our Postgres db. It is mounted to `./.dbt/` folder.

Profiles can contain multiple connections. We can create another output (connection) using the `world` dataset, which will be the one we use in this practice.

## Creating a model in dbt

For creating an example model, we can first test out a SQL script directly on the database.

```
SELECT cl.language
, ROUND(SUM(co.population*cl.percentage/100)::decimal,0) as amount
FROM (
	SELECT code
	, population
	FROM country
) co 
JOIN ( 
	SELECT countrycode
	, language
	, percentage
	FROM countrylanguage
) cl 
ON co.code = cl.countrycode
GROUP BY cl.language
ORDER BY amount desc
```

You can add this code as a sql file in the `models` folder - for simplicity, let's create a new folder named `world`. 

Create a new file called `languagespeakers.sql` and paste the SQL code into that file. To execute a model, we need to be in the dbt project folder. You can use the following bash commands:  
`ls` to list the contents of current directory. If you created the project with the name `dbt_practice` then you should see this as a folder.  
`cd dbt_practice` to navigate into this folder.  

There, you can execute the following command:

`dbt run -m languagespeakers` 

By default, `dbt run` would execute all models of the project. Using `-m` you can specify which models you would like to run.

You can now check that this view exists in the Postgres world database.

You can make modifications to your model and rerun to verify that the changes work.

## Modularizing sql code

The model folder can use a .yml file to add modular configurations and properties. Further info:  
https://docs.getdbt.com/reference/configs-and-properties 

You can name the .yml file whatever you would like. The naming convention used to be `schema.yml` 

```
version: 2

sources:
  - name: world_data
    database: world
    schema: public
    tables: 
      - name: city
      - name: country
      - name: countrylanguage
```

We can then replace the hardcoded table names by e.g. `{{source('world_data', 'country')}}`

We can modify the materialization. This is defined in `dbt_project.yml` but you can overwrite it at the top of a model's sql file by writing:

```
{{
    config(materialized='table')
}}
```

## Snapshotting

Let's create another model and name it as citypopulation.sql

```
SELECT CONCAT(country_name, '|', city_name) as id
, country_name
, city_name
, ROUND(city_pop/country_pop::decimal,3)*100 as perc_of_country_pop
, RANK() OVER (PARTITION BY country_name ORDER BY city_pop DESC) as city_rank_in_country
FROM 
(
	SELECT name as city_name
	, countrycode
	, population as city_pop
	FROM {{source('world_data','city')}}
) ci 
JOIN 
( 
	SELECT name as country_name
	, code
	, population as country_pop
	FROM {{source('world_data','country')}}
) co
ON ci.countrycode = co.code
```

What if any of the population figures change?  
That is a job for slowly changing dimensions, which in dbt can be invoked by using snapshots.

Let's create a snapshot file:

```
{% snapshot citypop_snapshot %}

{{
    config(
        target_database='world',
        target_schema='public',
        unique_key='id',
        strategy='check',
        check_cols=['perc_of_country_pop', 'city_rank_in_country']
    )
}}

SELECT * FROM {{ref('citypopulation')}}

{% endsnapshot %}
```

You can name the file also as `citypopulation.sql`, since this is a snapshot file and lives under `snapshots` folder.

We can then execute the snapshot by running:  

`dbt snapshot`

And we can then review the result in PGAdmin.  
We can try making some changes to the source tables and rerunning the snapshot to view the result.  
In a production setting, running the snapshots would be triggered e.g. every day or hour.  
Using snapshots, analysts can verify what was valid in the past at timestamp X.

## Referencing other models within a model

We can easily reference other models by using `ref`, the same way we did in the snapshot file.  
E.g. let's create a new model: 

```
SELECT country_name
, city_name
FROM {{ref('citypopulation')}}
WHERE city_rank_in_country = 1
```

This model is dependent on the *citypopulation* model.

## Generating documentation

`dbt docs generate`

`dbt docs serve`  
(in newer versions for this to work in Docker you may need to use `dbt docs serve --host 0.0.0.0`)

Running these commands starts up a webserver for viewing your database, tables, dependencies.