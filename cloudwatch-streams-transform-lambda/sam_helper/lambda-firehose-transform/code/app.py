
import os
import json
import base64
import requests
import time


def format_otel_metric(metric):
    """
    Format a single CloudWatch metric to OpenTelemetry format
    """
    # Convert CloudWatch timestamp (milliseconds) to nanoseconds
    timestamp_nano = int(metric['timestamp'] * 1e6)

    # Determine the metric type (assuming gauge for this example)
    metric_type = "gauge"

    # Create the metric data point

    data_point = {
        "timeUnixNano": timestamp_nano,
        "asDouble": metric['value'].get('max', 0.0),  # Using 'max' as an example
        "attributes": [
            {"key": k, "value": {"stringValue": v}}
            for k, v in metric.get('dimensions', {}).items()
        ]
    }

    # Add resource attributes
    resource_attributes = [
        {"key": "accountId", "value": {"stringValue": metric.get('account_id', '')}},
        {"key": "region", "value": {"stringValue": metric.get('region', 'useast1')}},
        {"key": "service.version", "value": {"stringValue": "1.0.0"}}
    ]

    metrics = {
        "name": "amazonaws.com/%s/%s" % (metric["namespace"], metric['metric_name']),
        "unit": metric.get('unit', 'Count'),
        "description": "",
        metric_type: {
            "dataPoints": [data_point]
        }
    }
    return metrics


def createOtelMetricPayload(metrics, region, accountId, streamArn):
    return {
        "resourceMetrics": [{
            "resource": {
                "attributes": [
                    {"key": "cloud.provider", "value": {"stringValue": "aws"}},
                    {"key": "cloud.account.id", "value": {"stringValue": accountId}},
                    {"key": "cloud.region", "value": {"stringValue": region}},
                    {"key": "aws.exporter.arn", "value": {"stringValue": streamArn}},
                    {"key": "service.name", "value": {"stringValue": "aws-cloudwatch-metrics"}},
                    {"key": "service.version", "value": {"stringValue": "1.0.0"}}
                ]
            },
            "scopeMetrics": [
                {
                    "scope": {
                        "name": "aws-cloudwatch-metrics.library",
                        "version": "1.0.0"
                    },
                    "metrics": metrics
                }
            ]
        }
    ]}


def sendMetrics(metrics, region, accountId, streamArn, endpoint):
    payload = createOtelMetricPayload(metrics, region, accountId, streamArn)
    print("Sending Metrics to OTEL Endpoint")

    try:
        response = requests.post(
            endpoint,
            timeout=5,
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        print("Metrics sent successfully: ", response.status_code)
    except requests.exceptions.RequestException as err:
        print("Error sending metrics: ", err)



def lambda_handler(event, context):
    """
    Amazon Data Firehose - Transformation Handler.

    This function should be invoked from a Firehose Transformation configuration.
    It expects cloudwatch metrics with JSON format.
    """

    endpoint = os.environ.get("endpoint", None)
    print("Endpoint: ", endpoint)
    if endpoint is None:
        print("Invalid Endpoint. Return without processing events")
        return {"records": event["records"]}

    streamArn = event["deliveryStreamArn"]
    region = event["region"]
    accountId = ""

    metrics = []

    try:
        for record in event["records"]:
            decodedData = base64.b64decode(record["data"]).decode().split("\n")

            for data in decodedData:
                try:
                    jData = json.loads(data)
                    accountId = jData.get('account_id', '')
                    otelData = format_otel_metric(jData)

                    metrics.append(otelData)
                except json.decoder.JSONDecodeError as err:
                    print("Failed to decode json string: ", err)
                    continue

            sendMetrics(metrics, region, accountId, streamArn, endpoint)

    except Exception as err:
        # Handle any errors
        print(f"Error processing records: {str(err)}")
        # Mark failed records

    return {'records': event['records']}

