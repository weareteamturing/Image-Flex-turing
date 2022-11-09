import argparse
import json
from collections import defaultdict
from functools import partial
import boto3

cloudfront_client = boto3.client("cloudfront")
lambda_client = boto3.client("lambda", region_name="us-east-1")


def get_distribution_config(dist_id):
    # get distribution config
    return cloudfront_client.get_distribution_config(Id=dist_id)


def update_distribution_cache_behavior(stage_config):
    dist_id = stage_config["DistributionId"]
    cache_behavior_config = stage_config["CacheBehavior_1"]

    dist_config = get_distribution_config(dist_id)

    nested_dict = lambda: defaultdict(partial(defaultdict, nested_dict))

    if not dist_config["DistributionConfig"]["CacheBehaviors"].get("Items"):
        dist_config["DistributionConfig"]["CacheBehaviors"]["Items"] = [{}]
        dist_config["DistributionConfig"]["CacheBehaviors"]["Quantity"] = 1
    dist_config["DistributionConfig"]["CacheBehaviors"]["Items"][
        0
    ] = cache_behavior_config
    response = cloudfront_client.update_distribution(
        Id=dist_id,
        IfMatch=dist_config["ETag"],
        DistributionConfig=dist_config["DistributionConfig"],
    )
    print("\033[32m" + "Updated CloudFront distribution" + "\033[0m")
    print("  status: " + str(response["ResponseMetadata"]["HTTPStatusCode"]))

    return response


def get_stage_config(stage):
    with open("image_flex_config.json") as f:
        image_flex_config = json.load(f)

    if stage == "dev":
        return image_flex_config["dev"]
    elif stage == "prod":
        return image_flex_config["prod"]


def set_stage_config(stage, updating_config):
    with open("image_flex_config.json") as f:
        image_flex_config = json.load(f)

    if stage == "dev":
        image_flex_config["dev"] = updating_config
    elif stage == "prod":
        image_flex_config["prod"] = updating_config

    with open("image_flex_config.json", "w") as f:
        json.dump(image_flex_config, f, indent=4, ensure_ascii=False)


def get_latest_lambda_arn(function_name):
    """Get the latest version of the Lambda function ARN."""
    response = lambda_client.list_versions_by_function(FunctionName=function_name)
    versions = response["Versions"]
    latest_version = sorted(versions, key=lambda x: x["Version"], reverse=True)[0]
    return latest_version["FunctionArn"]


def update_latest_lambda_arn_to_stage_config(stage_config):
    lambda_function_associations = stage_config["CacheBehavior_1"][
        "LambdaFunctionAssociations"
    ]["Items"]
    print("\033[32m" + f"LambdaFunctionAssociations" + "\033[0m")
    print(json.dumps(lambda_function_associations, indent=4))
    for lambda_function_association in lambda_function_associations:
        if lambda_function_association["EventType"] == "viewer-request":
            viewer_req_lambda_name = lambda_function_association[
                "LambdaFunctionARN"
            ].split(":")[-2]
            viewer_req_lambda_arn = get_latest_lambda_arn(viewer_req_lambda_name)
            lambda_function_association["LambdaFunctionARN"] = viewer_req_lambda_arn
        elif lambda_function_association["EventType"] == "origin-response":
            origin_resp_lambda_name = lambda_function_association[
                "LambdaFunctionARN"
            ].split(":")[-2]
            origin_resp_lambda_arn = get_latest_lambda_arn(origin_resp_lambda_name)
            lambda_function_association["LambdaFunctionARN"] = origin_resp_lambda_arn

    print("\033[32m" + "Updated Lambda ARN to latest" + "\033[0m")
    print("  viewer_req_lambda_arn: " + viewer_req_lambda_arn)
    print("  origin_resp_lambda_arn: " + origin_resp_lambda_arn)
    return stage_config


def update_stage_config(stage, mode="lambda_to_latest_arn"):
    stage_config = get_stage_config(stage)

    if mode == "lambda_to_latest_arn":
        stage_config = update_latest_lambda_arn_to_stage_config(stage_config)
        set_stage_config(stage, stage_config)


def view_stage_distribution_config(stage):
    dist_id = get_stage_config(stage)["DistributionId"]
    dist_config = get_distribution_config(dist_id)
    print("\033[32m" + "DistributionConfig" + "\033[0m")
    print(json.dumps(dist_config["DistributionConfig"], indent=4, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", help="stage name", type=str, choices=["dev", "prod"])
    parser.add_argument("mode", help="mode", type=str, choices=["update", "view"])

    args = parser.parse_args()
    print("\033[34m" + "\033[1m" + "Stage: " + args.stage + "\033[0m")

    if args.mode == "update":
        # change image_flex_config.json (local)
        update_stage_config(args.stage, mode="lambda_to_latest_arn")

        # update CloudFront distribution (AWS)
        update_distribution_cache_behavior(get_stage_config(args.stage))
    else:
        view_stage_distribution_config(args.stage)


if __name__ == "__main__":
    main()
