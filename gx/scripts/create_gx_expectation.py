import great_expectations as gx

# Retrieve the a suite
context = gx.get_context()
existing_suite_name = (
    "transaction_expectation_suite" 
)
suite = context.suites.get(name=existing_suite_name)


# Examples: Create and add an expectation to the suite  
# # currency
# suite.add_expectation(
#     gx.expectations.ExpectColumnValuesToMatchRegex(column="currency", regex=r"^[A-Z]{3}$")
# )

# # customer_id
# suite.add_expectation(
#     gx.expectations.ExpectColumnValuesToNotBeNull(column="customer_id")
# )