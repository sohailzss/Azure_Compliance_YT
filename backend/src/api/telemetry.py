# Azure opentelementry integration

import os
from azure.monitor.opentelemetry import configure_azure_monitor
import logging 

# Create a dedicated logger

logger = logging.getlogger("brand-guardian-telemetry")

def setup_telemetry():

    '''
    Initializes Azure monitor Opentelmetry
    Tracks: Https request, database queries, errors, performance metric
    Sends the data to azure monitor

    it auto captures every API requests
    No need to manually log each endpoint


    '''

    # retrieve the connection string

    connection_string  = os.getenv("ALLICATIONINSIGHTS_CONNECTION_STRING")

    # CHECK THE CONFIGURE
    if not connection_string:
        logger.warning("No instrumentation key found. telemetry is disabled.")
        return
    # configure the azure monitor
    try:
        configure_azure_monitor(
            connection_string=connection_string
            logger_name = "brand_guardian_tracer"
        )
        logger.info("Azure monitor tracking enabled and connected")

    except Exception as e:
        logger.error("Failed to initialize Azure monitor: {e}")

        