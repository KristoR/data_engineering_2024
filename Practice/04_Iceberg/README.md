
## Walkthrough

### Working with parquet files. 

Download a json file:
https://data.nasa.gov/resource/gh4g-9sfh.json?$offset=0

Upload it to minio using minio UI in the browser  
`localhost:9001`  
(alternatives: client `mc`, python package `minio`)  

We can now query it from duckdb. 

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
df = conn.sql(f"SELECT * FROM read_json('{s3_url}')").arrow()
``` 

We can also write back to S3. When we partition the parquet file, observe the folder structure.

`conn.sql("COPY (SELECT name,id FROM tmp) TO 's3://practice-bucket/test.parquet' (FORMAT PARQUET, PARTITION_BY (year))")`

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

Make a folder `./iceberg_catalog` in your duckdb data folder.  

Add a file `.pyiceberg.yaml` in your duckdb data folder. 

With the content:  
```
catalog:
  local:
    uri: sqlite:///iceberg_catalog/catalog.db
    warehouse: file://iceberg_catalog
```

In Python, execute the following:
```
import os

os.environ['PYICEBERG_HOME'] = os.getcwd()
```

```
from pyiceberg.catalog import load_catalog

catalog = load_catalog(name='local')
```

You can view the catalog information:  
`print(catalog.properties)`

Creating a table 
```
from pyiceberg.schema import Schema
from pyiceberg.types import NestedField, IntegerType, StringType

schema = Schema(
  NestedField(field_id=1, name='id', field_type=IntegerType(), required=True),
  NestedField(field_id=2, name='name', field_type=StringType(), required=True),
)
```

### Task:
Read data and write data to the Iceberg catalog using `duckdb`, `pyiceberg` and `pyarrow` packages.