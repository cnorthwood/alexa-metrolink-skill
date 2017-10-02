#!/usr/bin/env bash

set -e

STACK_NAME="alexa-metrolink-skill"

cd "$(dirname "$0")"

if [ -z "`which jq`" ] ; then
    echo "Please install jq"
    exit 1
fi

echo -n "Creating package..."

rm -f alexa_metrolink_skill.zip
cd virtualenv/lib/python3.6/site-packages/
zip -r9 ../../../../alexa_metrolink_skill.zip * >/dev/null
cd ../../../../
zip -g alexa_metrolink_skill.zip alexa_metrolink_skill.py >/dev/null
zip -g alexa_metrolink_skill.zip stop-names.json >/dev/null

echo " ✅"

version="`date +%Y%m%d.%H%M%S`"

echo -n "Generating CloudFormation template..."
infrastructure/cloudformation.py
echo " ✅"

echo -n "Finding code bucket..."
deployment_bucket=`virtualenv/bin/aws cloudformation describe-stack-resource \
    --stack-name $STACK_NAME \
    --logical-resource-id "MetrolinkSkillLambdaBucket" \
    | jq -r .StackResourceDetail.PhysicalResourceId`

if [ "$deployment_bucket" == "" ] ; then
    echo " ❎"
    echo -n "Unable to find code bucket, doing create-stack..."
    virtualenv/bin/aws cloudformation deploy \
        --stack-name $STACK_NAME \
        --template-file infrastructure/cloudformation.json \
        --capabilities CAPABILITY_IAM
    deployment_bucket=`virtualenv/bin/aws cloudformation describe-stack-resource \
        --stack-name $STACK_NAME \
        --logical-resource-id "MetrolinkSkillLambdaBucket" \
        | jq -r .StackResourceDetail.PhysicalResourceId`
    echo " ✅"
else
    echo " ✅"
fi


echo -n "Uploading code..."
virtualenv/bin/aws s3 cp alexa_metrolink_skill.zip s3://$deployment_bucket/$version/alexa_metrolink_skill.zip
echo " ✅"

echo "Updating Lambda deployment..."
virtualenv/bin/aws cloudformation deploy \
    --stack-name $STACK_NAME \
    --template-file infrastructure/cloudformation.json \
    --parameter-overrides Version=$version \
    --capabilities CAPABILITY_IAM
echo " ✅"

# TODO: script changes to interaction model (if possible)
