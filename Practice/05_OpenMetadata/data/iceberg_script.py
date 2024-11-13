import duckdb
from pyiceberg.catalog import load_catalog
from pyiceberg.exceptions import NamespaceAlreadyExistsError, TableAlreadyExistsError


catalog = load_catalog(name="rest")

def create_schema_and_tables(namespace, data_files):
  """
  Helper function for creating namespace and tables.
  """
  try:
    catalog.create_namespace(namespace)
  except NamespaceAlreadyExistsError:
    print(f"Namespace {namespace} already exists, continuing.") 
  for _f in data_files:
    arrow_table = duckdb.sql(f"SELECT * FROM {_f}").arrow()
    schema = arrow_table.schema
  
    table_name = _f.split(".")[0]
    try:
      table = catalog.create_table(
        identifier=f"{namespace}.{table_name}",
        schema=schema,
      )
    except TableAlreadyExistsError:
      print(f"Table {namespace}.{table_name} already exists, continuing.") 
      table = catalog.load_table(f"{namespace}.{table_name}")
      with table.update_schema() as update:
        update.union_by_name(schema)
    table.overwrite(arrow_table)


# create the staging layer
namespace = "staging"
data_files = ["sales_customer.parquet","sales_product.parquet","sales_staff.parquet"]
create_schema_and_tables(namespace,data_files)

# create the warehouse layer
namespace = "dwh"
data_files = ["DIM_customer.parquet","DIM_manufacturer.parquet","DIM_salesperson.parquet","DIM_date.parquet","DIM_model.parquet","FACT_carsales.parquet"]
create_schema_and_tables(namespace,data_files)