import json

import cw_metric_helper


def lambda_handler(event, context):
    cwHelper = cw_metric_helper.CloudWatch(region="us-east-1")
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

    print("Ret: ", ret)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "hello cloudwatch monitor",
        }),
    }
