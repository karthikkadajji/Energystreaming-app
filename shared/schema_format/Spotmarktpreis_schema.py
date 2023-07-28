# Define the Avro schema in a separate module
SCHEMA_JSON = {
    "type": "record",
    "name": "SpotMarketPreisEventData",
    "namespace": "com.example",
    "fields": [
        {"name": "Datum", "type": "string"},
        {"name": "von", "type": "string"},
        {"name": "Zeitzone_von", "type": "string"},
        {"name": "bis", "type": "string"},
        {"name": "Zeitzone_bis", "type": "string"},
        {"name": "Spotmarktpreis_in_ct_kWh", "type": "string"},
    ]
}
