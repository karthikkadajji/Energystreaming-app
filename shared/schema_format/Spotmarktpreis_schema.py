# Define the Avro schema in a separate module
SCHEMA_JSON = """
{"type": "record",
 "name": "spotmarktpreis",
 "fields": [
     {"name": "Datum", "type": "string"},
     {"name": "von", "type": "string"},
     {"name": "Zeitzone von", "type": "string"},
     {"name": "bis", "type": "string"},
     {"name": "Zeitzone bis", "type": "string"},
     {"name": "Spotmarktpreis in ct/kWh", "type": "string"}
    ]
}"""