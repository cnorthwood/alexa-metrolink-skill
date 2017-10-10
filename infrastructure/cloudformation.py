#!virtualenv/bin/python3

from awacs.aws import Action, Statement, Allow, Policy, Principal
import os
from troposphere import Template, Ref, GetAtt, Join, Parameter, If, Equals, Output
from troposphere.iam import Role
from troposphere.awslambda import Function, Code, Permission, Environment
from troposphere.s3 import Bucket

template = Template()

version = template.add_parameter(Parameter("Version", Type="String", Default="0"))
app_id = template.add_parameter(Parameter("AlexaApplicationId", Type="String"))

template.add_condition("Bootstrapping", Equals(Ref(version), "0"))

bucket = template.add_resource(Bucket(
    "MetrolinkSkillLambdaBucket",
))

lambda_role = template.add_resource(Role(
    "MetrolinkSkillExecutionRole",
    Path='/',
    AssumeRolePolicyDocument=Policy(
        Statement=[
            Statement(
                Effect=Allow,
                Principal=Principal(
                    'Service',
                    ['lambda.amazonaws.com']
                ),
                Action=[Action('sts', 'AssumeRole')]
            )
        ]
    )
))

skill = template.add_resource(Function(
    "MetrolinkSkill",
    Code=If(
        "Bootstrapping",
        Code(ZipFile="placeholder"),
        Code(
            S3Bucket=Ref(bucket),
            S3Key=Join('/', [Ref(version), 'alexa_metrolink_skill.zip'])
        )
    ),
    Environment=Environment(
        Variables={
            'ALEXA_APP_ID': Ref(app_id)
        }
    ),
    Handler='alexa_metrolink_skill.handle_request',
    Role=GetAtt(lambda_role, 'Arn'),
    Runtime='python3.6'
))

template.add_output(Output(
    "SkillLambdaArn",
    Value=GetAtt(skill, 'Arn')
))

skill_permission = template.add_resource(Permission(
    "AlexaPermission",
    FunctionName=Ref(skill),
    Action='lambda:InvokeFunction',
    Principal='alexa-appkit.amazon.com'
))

with open(os.path.join(os.path.dirname(__file__), 'cloudformation.json'), 'w') as template_file:
    template_file.write(template.to_json(indent=2))
