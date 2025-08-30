#!/usr/bin/env python
# -*- coding: utf-8 -*-

import boto3
from collections import defaultdict
from typing import Dict, List, Optional, Any


class CloudWatch():
    def __init__(self, profileName=None, region="us-east-1"):
        """
        Initialize CloudWatch Helper class.
        """

        if profileName is not None:
            session = boto3.Session(profile_name=profileName, region_name=region)
        else:
            session = boto3.Session(region_name=region)

        self.client = session.client("cloudwatch")

    def list_metrics(self):
        kwargs = {
            "IncludeLinkedAccounts": True
        }
        result = {
            "Metrics": [],
            "Summary": {
                "TotalMetricCount": 0
            }
        }

        done = False
        nextToken = None
        while not done:
            if nextToken is None:
                data = self.client.list_metrics(**kwargs)
            else:
                data = self.client.list_metrics(**kwargs, NextToken=nextToken)

            # mesh account id into metric
            idx = 0
            owningAccounts = data["OwningAccounts"]
            for metric in data["Metrics"]:
                accountId = owningAccounts[idx]
                metric["aws.accountId"] = accountId
                idx += 1
                if result["Summary"].get(accountId, None) is None:
                    result["Summary"][accountId] = {}
                    result["Summary"][accountId]["TotalMetricCount"] = 0
                    result["Summary"][accountId]["MetricCountByNamespace"] = defaultdict(int)
                    result["Summary"][accountId]["UniqueMetricNames"] = set()

                result["Summary"]["TotalMetricCount"] += 1
                result["Summary"][accountId]["TotalMetricCount"] += 1
                result['Summary'][accountId]['UniqueMetricNames'].add(metric['MetricName'])
                result["Summary"][accountId]["MetricCountByNamespace"][metric["Namespace"]] += 1

                result["Metrics"].append(metric)

            if "NextToken" in data.keys():
                nextToken = data["NextToken"]
            else:
                done = True

        return result

    def put_metric_data(self, namespace: str, 
                        metric_name: str, value: float, 
                        unit: str = 'Count', 
                        dimensions: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Push a metric to CloudWatch.

        Args:
            namespace: Namespace for the metric
            metric_name: Name of the metric
            value: Value of the metric
            unit: Unit of the metric
            dimensions: List of dimensions for the metric

        Returns:
            Response from CloudWatch API
        """
        metric_data = {
            'MetricName': metric_name,
            'Value': value,
            'Unit': unit
        }
        print("BRD: dimensions: ", dimensions)
        print("BRD: metric data: ", metric_data)

        if dimensions:
            metric_data['Dimensions'] = dimensions
        
        response = self.client.put_metric_data(
            Namespace=namespace,
            MetricData=[metric_data]
        )
        
        return {
            'Status': 'Success',
            'Response': response,
            'MetricDetails': {
                'Namespace': namespace,
                'MetricName': metric_name,
                'Value': value,
                'Unit': unit,
                'Dimensions': dimensions or []
            }
        }







