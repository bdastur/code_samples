#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
import unittest
from code import app
from code import cw_metric_helper

class TestApp(unittest.TestCase):
    def test_basic(self):
        cwHelper = cw_metric_helper.CloudWatch(profileName="brd3", region="us-east-1")

        result = cwHelper.list_metrics()
        print(result)
        for key in result["Summary"]:
            if key == "TotalMetricCount":
                continue
            # push metrics.

            print("Key: ", key)
            totalMetricCount = result["Summary"][key]["TotalMetricCount"]
            dimensions = []
            dimensions.append({"Name": "accountId", "Value": key})

            print("Dimension: %s, totalmetriccount: %s" % (dimensions, totalMetricCount))

            ret = cwHelper.put_metric_data(
                    namespace="testnamespace",
                    metric_name="testmetric",
                    value=totalMetricCount,
                    unit="Count",
                    dimensions=dimensions)


