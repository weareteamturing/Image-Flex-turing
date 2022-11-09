#!/bin/sh

# Lambda@edge log group이 보이지 않아 debugging이 불가능할 때,
# 해당 lambda의 log group을 찾아주는 스크립트 

# Ref: https://github.com/walkermatt/dotbin/blob/master/find-lambda-edge-logs
# Inspired by https://stackoverflow.com/a/54096479/526860

FUNCTION_NAME=$1

if [ $FUNCTION_NAME ] && [ $FUNCTION_NAME != '--help' ]
then
    for region in $(aws --output text  ec2 describe-regions | cut -f 4) 
    do
        for loggroup in $(aws --output text  logs describe-log-groups --log-group-name "/aws/lambda/us-east-1.$FUNCTION_NAME" --region $region --query 'logGroups[].logGroupName')
        do
            echo $region $loggroup
        done
    done
else
    echo "Usage:"
    echo ""
    echo "find-lambda-edge-logs FUNCTION_NAME"
    echo ""
    echo "To specify a profile set the AWS_PROFILE environment variable."
    exit 1
fi