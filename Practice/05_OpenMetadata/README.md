
## Starting the services
Run `docker compose up -d`

Note: this can take several minutes. You can observe the status in the CLI or Docker Desktop. 

The last service to start should be `openmetadata_server`. Once it starts, it can take an additional 1-2 minutes for the UI to be usable.

## Preparing Iceberg tables
Move or copy files from `./data` to `../mnt/tmp/05_openmetadata/duckdb_data`, e.g. in bash:  
`cp ./data/* ../mnt/tmp/05_openmetadata/duckdb_data/`

Make sure to include the `.pyiceberg.yaml` file:  
`cp ./data/.pyiceberg.yaml ../mnt/tmp/05_openmetadata/duckdb_data/`

Go into the DuckDB container and initiate the iceberg script.
`docker exec -it duckdb bash`  

In the container:  
`cd data`  
`python iceberg_script.py`  

You should now have 2 schemas and a total of 9 tables in Iceberg.

## OpenMetadata UI
The OpenMetadata UI is accessible from `localhost:8585`.  If it doesn't open, then it might be that not all services have started. Check in CLI or Docker Desktop if `openmetadata_server` has started.  
`localhost:8586` for a simple Admin view.

OpenMetadata offers a lot of functionalities for various aspects of data governance.  
For the purpose of your project, you should minimally add `descriptions` on columns and define `lineage` between tables.  

Let's first look at how to connect to Iceberg. 

## Setting up connection to Iceberg
Settings --> Services --> Databases --> Add New Service --> Iceberg 

The name is up to you, what is important are the following connection parameters:  
Connection: `RestCatalogConnection`   
URI: `http://iceberg_rest:8181`  
Client ID/Secret: `minioadmin`  

You can then see the Iceberg tables under `Explore` in the UI, or search for the tables.  
For further information what you can do: https://docs.open-metadata.org/latest/how-to-guides

## Sample data

The associated Airflow service comes with some preset pipelines. You can enable these from the Airflow UI:  
`localhost:8080`  
`admin` for user/pass