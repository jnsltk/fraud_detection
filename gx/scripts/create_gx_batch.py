'''
    Made by: Shiyao Xin
'''

import great_expectations as gx
from great_expectations import expectations as gxe


context = gx.get_context()

# Retrieve data asset
data_source_name = "dataset_sample.csv"
data_asset_name = "transaction_csv_file"
file_data_asset = context.data_sources.get(data_source_name).get_asset(data_asset_name)

# Retrieve a batch of sample data
batch_definition_name = "transaction_sample.csv"
batch_definition_path = "dataset_sample.csv"
batch_definition = file_data_asset.add_batch_definition_path(
    name=batch_definition_name, path=batch_definition_path
)

batch = batch_definition.get_batch()
# print(batch.head())

