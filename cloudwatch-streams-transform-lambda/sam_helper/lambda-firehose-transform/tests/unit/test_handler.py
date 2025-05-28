import json

import pytest

from code import app



@pytest.fixture()
def setupFireHoseEvent():
    fireHoseEvent = {
        "deliveryStreamArn": "arn:aws:firehose:us-east-1:168442441230:deliverystream/MetricStreams-cwmetrics-stream-json-1-3cpNgpuC",
        "region": "us-east-1",
        "records": []
    }

    fileName = "./testdata/shard_data"

    with open(fileName, "r") as inFile:
        record = {}
        record["recordId"]: "shardId-xxxx"
        record["data"] = inFile.read()

        fireHoseEvent["records"].append(record)

    return fireHoseEvent


def test_lambda_handler(setupFireHoseEvent):

    ret = app.lambda_handler(setupFireHoseEvent, "")
    print("ret: ", ret)

    #data = json.loads(ret["body"])
    #assert ret["statusCode"] == 200
    #assert "message" in ret["body"]
    #assert data["message"] == "hello world"
