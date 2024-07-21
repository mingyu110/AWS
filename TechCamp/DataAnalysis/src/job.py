import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame

# Initialize GlueContext
sc = SparkContext.getOrCreate()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)

# Define input and output paths
input_path = "s3://glue-xml-file/"
output_path = "s3://glue-parquet-file/"

# Read XML data as DynamicFrame
xml_dynamic_frame = glueContext.create_dynamic_frame.from_catalog(database="glue-etl", table_name="xml_glue_xml_file")

# Convert specific data types to string using Spark SQL functions
xml_dynamic_frame_df = xml_dynamic_frame.toDF()

# Write data to Parquet format
glueContext.write_dynamic_frame.from_options(
    frame=DynamicFrame.fromDF(xml_dynamic_frame_df, glueContext, "transformed_df"), connection_type="s3",
    connection_options={"path": output_path}, format="parquet", mode="overwrite")

# Commit the job
job.commit()
