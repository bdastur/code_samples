#!/bin/bash 

echo "Bash Template"

function usage () {
    echo "Example usage: "
    echo "sam deploy --parameter-overrides subnet1A=subnet-xxxx subnet1B=subnet-xxxx SecurityGroupDefault=sg-xxxx CollectorEndpoint=\"http://private-lb-xxx.us-east-1.amazonaws.com:80/v1/metrics\""
    exit 1
}

subnet1A=$1
subnet1B=$2
securityGroupId=$3
endpoint=$4

if [[ -z $subnet1A ]]; then
    usage
fi

if [[ -z $subnet1B ]]; then
    usage
fi

if [[ -z $securityGroupId ]]; then
    usage
fi

if [[ -z $endpoint ]]; then
    usage
fi


sam deploy --parameter-overrides subnet1A=${subnet1A} subnet1B=${subnet1B} SecurityGroupDefault=${securityGroupId} CollectorEndpoint="${endpoint}"



