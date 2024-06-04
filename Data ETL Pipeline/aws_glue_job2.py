import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

glueContext = GlueContext(SparkContext.getOrCreate())

customersDF = glueContext.create_dynamic_frame.from_catalog(
    database="datadb",
    table_name="raw_customers")
glueContext.write_dynamic_frame.from_options(customersDF, connection_type = "s3", connection_options = {"path": "s3://jack-dataset/cleansed/customers"}, format = "parquet")