import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

glueContext = GlueContext(SparkContext.getOrCreate())

customerDF = glueContext.create_dynamic_frame.from_catalog(
    database="datadb",
    table_name="src_postgres_public_customers", redshift_tmp_dir="s3://jack-dataset/scripts/")

glueContext.write_dynamic_frame.from_options(customerDF, connection_type = "s3", connection_options = {"path": "s3://jack-dataset/raw/customers"}, format = "csv")