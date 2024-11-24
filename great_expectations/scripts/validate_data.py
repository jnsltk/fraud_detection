import great_expectations as gx

context = gx.get_context()

file_path = "prototypes/data/dataset_sample.csv"
batch = context.data_sources.pandas_default.read_csv(file_path)

# Retrieve a Batch Definition
data_source_name = "dataset_sample.csv"
data_asset_name = "transaction_csv_file"
batch_definition_name = "transaction_sample.csv"

batch_definition = (
    context.data_sources.get(data_source_name)
    .get_asset(data_asset_name)
    .get_batch_definition(batch_definition_name)
)

# Retrieve a Validation Definition
validation_definition_name = "my_validation_definition"
validation_definition = context.validation_definitions.get(validation_definition_name)

# Run the validation
validation_results = validation_definition.run()

# Log the results
print(validation_results)
if not validation_results["success"]:
     print("Validation Failed!")
print("CSV Validation Passed!")