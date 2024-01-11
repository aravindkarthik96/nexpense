from google.cloud import bigquery

def create_sheet_ids_table() :
    client = bigquery.Client()

    table_id = "transactions-409516.user_store.user_to_sheet_id_mapping"

    schema = [
        bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("sheet_id", "INTEGER", mode="REQUIRED"),
    ]

    table = bigquery.Table(table_id, schema=schema)
    table = client.create_table(table)  # Make an API request.
    print(
        "Created table {}.{}.{}".format(table.project, table.dataset_id, table.table_id)
    )