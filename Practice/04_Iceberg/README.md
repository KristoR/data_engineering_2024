
## Walkthrough

### Working with parquet files. 

Download a json file:
https://data.nasa.gov/resource/gh4g-9sfh.json?$offset=0

Upload it to minio using minio UI in the browser  
`localhost:9001`  
(alternatives: client `mc`, python package `minio`)  

Note: first create a bucket, e.g., `practice-bucket` with default options.

We can now query this JSON file from duckdb. 

Exec into the container  
`docker exec -it duckdb bash`

Change to correct folder  
`cd data/`

Start python interpreter   
`python`

Run following commands (you can run line by line or alltogether)  
```
import duckdb
conn = duckdb.connect() # use duckdb.co
conn.install_extension("httpfs")
conn.load_extension("httpfs")
conn.sql("""
SET s3_region='us-east-1';
SET s3_url_style='path';
SET s3_endpoint='minio:9000';
SET s3_access_key_id='minioadmin' ;
SET s3_secret_access_key='minioadmin';
SET s3_use_ssl=false;
""")

bucket_name = "practice-bucket"
file_name = "gh4g-9sfh.json"
s3_url = f"s3://{bucket_name}/{file_name}"

# Read data from the MinIO bucket using DuckDB into a pyarrow dataframe
conn.sql(f"SELECT * FROM read_json('{s3_url}')")

# Create a table named "tmp" based on the JSON data.
conn.sql(f"CREATE TABLE tmp AS SELECT * FROM read_json('{s3_url}')")
``` 

We can also write back to S3. When we partition the parquet file, observe the folder structure.

Copy entire table:  
`conn.sql("COPY tmp TO 's3://practice-bucket/test.parquet' (FORMAT PARQUET)")`

Copy the result of a query:  
`conn.sql("COPY (SELECT id, name FROM tmp) TO 's3://practice-bucket/test.parquet' (FORMAT PARQUET)")`

Copy as a partitioned parquet file:  
`conn.sql("COPY tmp TO 's3://practice-bucket/partition_by_year.parquet' (FORMAT PARQUET, PARTITION_BY (year))")`

We can test various writing strategies
`conn.sql("COPY (SELECT * FROM tmp WHERE year LIKE '200%') TO 's3://practice-bucket/partition_by_year.parquet' (FORMAT PARQUET, PARTITION_BY (year))")`  
Default: error

Overwrite or ignore:  
`conn.sql("COPY (SELECT * FROM tmp WHERE year LIKE '200%') TO 's3://practice-bucket/partition_by_year.parquet' (FORMAT PARQUET, PARTITION_BY (year), OVERWRITE_OR_IGNORE)")`

Append:  
`conn.sql("COPY (SELECT * FROM tmp WHERE year LIKE '200%') TO 's3://practice-bucket/partition_by_year.parquet' (FORMAT PARQUET, PARTITION_BY (year), APPEND)")`

Read a partitioned parquet file:  
`conn.sql("SELECT * FROM read_parquet('s3://practice-bucket/partition_by_year.parquet/**')")`


## Iceberg

Add the following as a `.pyiceberg.yaml` in your `duckdb_data` folder:  
```
catalog:
  rest:
    uri: http://iceberg_rest:8181/
    s3.endpoint: http://minio:9000
    s3.access-key-id: minioadmin
    s3.secret-access-key: minioadmin
    warehouse: warehouse
```

Run the following 
```
from pyiceberg.catalog import load_catalog
from pyiceberg.schema import Schema, NestedField
from pyiceberg.types import IntegerType, StringType
import pyarrow as pa

catalog = load_catalog(name="rest")
namespace = "default"
table_name = "tmp_table"
catalog.create_namespace(namespace)

arrow_table = conn.sql("SELECT * FROM tmp").arrow()
schema = arrow_table.schema

table = catalog.create_table(
    identifier=f"{namespace}.{table_name}",
    schema=schema,
)

table.append(arrow_table)

```

To read data in DuckDB, we need to store the PyIceberg table as an Arrow table.  

```
arrow_table_read_example = table.scan().to_arrow()
```

We can now query this variable directly in DuckDB.

```
conn.sql("SELECT * FROM arrow_table_read_example")
```


For getting the table snapshot at a specific timestamp you can use `table.snapshot_as_of_timestamp`  
(https://py.iceberg.apache.org/reference/pyiceberg/table/#pyiceberg.table.Table.snapshot_as_of_timestamp)

Or you can query it based on the snapshot id `table.snapshot_by_id`  
(https://py.iceberg.apache.org/reference/pyiceberg/table/#pyiceberg.table.Table.snapshot_by_id)

```
for snapshot in table.snapshots():
    print(f"Snapshot ID: {snapshot.snapshot_id}, Timestamp: {snapshot.timestamp_ms}")
```

If you want to restore to a previous version, you can use the table scan based on the snapshot id and overwrite the table.   
```
snapshot_id = # fill me
table.overwrite(table.scan(snapshot_id=snapshot_id).to_arrow())
```

You can also view the manifest files from Minio UI.

For a more comprehensive overview:  
https://py.iceberg.apache.org/api/


