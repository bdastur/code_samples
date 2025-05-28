# CloudWatch Metric Streams - Firehose Lambda 

This project demonstrates a proof of concept for streaming CloudWatch metrics to an 
OpenTelemetry collector using Amazon Kinesis Firehose and AWS Lambda.

## Architecture


![Architecture Diagram](https://raw.githubusercontent.com/bdastur/code_samples/refs/heads/main/cloudwatch-streams-transform-lambda/docs/cwmetrics_streaming.drawio.png)


## Components

- **CloudWatch Metric Stream**: Streams metrics in real-time
- **Kinesis Firehose**: Delivers metrics to Lambda for transformation
- **Lambda Function**: Transforms CloudWatch metrics to OpenTelemetry format
- **Network LoadBalancer**: Network Loadbalancer 
- **OpenTelemetry Collector**: Receives and processes metrics - Running in Docker on an EC2 instance


## Prerequisites

- AWS Account with appropriate permissions
- OpenTelemetry Collector endpoint
- Python 3.11+
- Terraform (for infrastructure deployment)
- SAM cli 

## Setup

1. Setup Infrastructure using terraform.
   This will create VPC, subnet, security groups.

⚠️ **Note:**  
Automation lacks the followng today and will need to be created.
- Create a cloudwatch stream, with stream to Firehose
- Create an EC2 instance and setup OTEL collector (Steps in next section)
- Create a NLB in VPC and private subnet.

2. Create the Transformation Lambda function.

```
cd sam_helpers/lambda-firehose-transform

# setup lambda layer folder.
sam build
./setup_layer.sh

./deploy_lambda.sh <subnet 1> <subnet 2> <sg> <endpoint>

```

3. Configure Firehose transformation using the Lambda function.


## Lambda Function

The Lambda function performs the following:
- Receives CloudWatch metrics from Firehose
- Transforms metrics to OpenTelemetry format
- Sends metrics to OpenTelemetry collector


### Example Transformation

Input (CloudWatch Format):
```json
{'account_id': '1xxxxxxxxxxx0',
 'dimensions': {'ClusterName': 'graviton-perf-lab',
                'FullPodName': 'k8sgpt-operator-controller-manager-6458589df6-lkz6b',
                'Namespace': 'k8sgpt-operator-system',
                'PodName': 'k8sgpt-operator-controller-manager'},
 'metric_name': 'pod_network_rx_bytes',
 'metric_stream_name': 'cwmetrics-stream-json-1',
 'namespace': 'ContainerInsights',
 'region': 'us-east-1',
 'timestamp': 1747775760000,
 'unit': 'Bytes/Second',
 'value': {'count': 1.0, 'max': 0.0, 'min': 0.0, 'sum': 0.0}}
```

Output (OpenTelemetry Format):
```json
{'resourceMetrics': 
  [{'resource': 
    {'attributes': [{'key': 'cloud.provider',
                     'value': {'stringValue': 'aws'}},
                      {'key': 'cloud.account.id',
                       'value': {'stringValue': '1xxxxxx'}},
                      {'key': 'cloud.region',
                       'value': {'stringValue': 'us-east-1'}},
                      {'key': 'aws.exporter.arn',
                       'value': {'stringValue': 'arn:aws:firehose:us-east-1:1xxxxxxx0:deliverystream/MetricStreams-cwmetrics-stream-json-1-xxxx'}},
                      {'key': 'service.name',
                       'value': {'stringValue': 'aws-cloudwatch-metrics'}},
                      {'key': 'service.version',
                       'value': {'stringValue': '1.0.0'}}]},
                      'scopeMetrics': [{'metrics': [{'description': '',
                                      'gauge': {'dataPoints': [{'asDouble': 0.03146602896352609,
                                                 'attributes': [{'key': 'ClusterName',
                                                                'value': {'stringValue': 'test-cluster'}},
                                                                  {'key': 'ServiceName',
                                                                   'value': {'stringValue': 'simple-App-3'}}],
                                                   'timeUnixNano': 1747775640000000000}]},
                                                     'name': 'amazonaws.com/ECS/ContainerInsights/TaskCpuUtilization',
                                                     'unit': 'Percent'},
                                                    {'description': '',
                                                     'gauge': {'dataPoints': [{'asDouble': 0.0,
                                                         'attributes': [{'key': 'ClusterName',
                                                                   'value': {'stringValue': 'graviton-perf-lab'}},
                                                                  {'key': 'FullPodName',
                                                                   'value': {'stringValue': 'k8sgpt-operator-controller-manager-6458589df6-lkz6b'}},
                                                                  {'key': 'Namespace',
                                                                   'value': {'stringValue': 'k8sgpt-operator-system'}},
                                                                  {'key': 'PodName',
                                                                   'value': {'stringValue': 'k8sgpt-operator-controller-manager'}}],
                                                   'timeUnixNano': 1747775760000000000}]},
                         'name': 'amazonaws.com/ContainerInsights/pod_network_rx_bytes',
                         'unit': 'Bytes/Second'},

:
]}
```

## Otel Configuration

```
[root@ip-10-0-101-84 otelcollector]# more docker-compose.yaml 
services:
  otel-collector:
    image: otel/opentelemetry-collector-contrib
    volumes:
      - ./otel-collector-config.yaml:/etc/otelcol-contrib/config.yaml
    ports:
      - 1888:1888 # pprof extension
      - 8888:8888 # Prometheus metrics exposed by the Collector
      - 8889:8889 # Prometheus exporter metrics
      - 13133:13133 # health_check extension
      - 4317:4317 # OTLP gRPC receiver
      - 4318:4318 # OTLP http receiver
      - 55679:55679 # zpages extension
[root@ip-10-0-101-84 otelcollector]# 
[root@ip-10-0-101-84 otelcollector]# 
--------------------------------------------------------------------------------
[root@ip-10-0-101-84 otelcollector]# more otel-collector-config.yaml 
# /tmp/otel-collector-config.yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318
exporters:
  # NOTE: Prior to v0.86.0 use `logging` instead of `debug`.
  debug:
    verbosity: detailed
processors:
  batch:
service:
  pipelines:
    traces:
      receivers: [otlp]
      exporters: [debug]
      processors: [batch]
    metrics:
      receivers: [otlp]
      exporters: [debug]
      processors: [batch]
    logs:
      receivers: [otlp]
      exporters: [debug]
      processors: [batch]
--------------------------------------------------------------------------------

> docker-compose up



### IAM Permissions

The Lambda function requires:
- Basic Lambda execution permissions
- Access to CloudWatch logs
- Network access to OpenTelemetry collector


Note: This is a proof of concept and may need additional security and error handling for production use.
