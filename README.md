# Image-Flex by teamturing
Add on-demand image resizing to CloudFront using Lambda@Edge.
Forked and modified from [Image-Flex](https://github.com/HoraceShmorace/Image-Flex)
### Features
* Quick deployment of lambda edge functions for image resizing
  * viewer-request : `UriToS3Key`
  * origin-response : `GetOrCreateImage`
* Managing create / update Cache-Behavior for CloudFront Distribution
  * `image_flex_config.json`
### Difference from Image-Flex (original repo)
* Simplified CloudFormation stack
  * Only `EdgeLambdaRole`, `OriginAccessId`, `UriToS3KeyFunction` `GetOrCreateImageFunction` are created
* Can be used with existing CloudFront Distribution
* Limit upper bound of image size
  * if width or height is larger than `2000` then return original image
  
## Quick Start
### 1. Deploy Lambda Function
```bash
npm run setup -- dev
npm run update -- dev
```

1. `setup`
   * create CloudFormation deployment bucket for designated stage (execute once per stage)
2. `update`
   * build, package, and deploy the application stack to CloudFormation using the AWS SAM CLI. 
  
if `update` is successful, 2 lambda functions will be created in us-east-1 region
   * `tcms-image-flex-{stage}-tcms-UriToS3Key`
   * `tcms-image-flex-{stage}-tcms-GetOrCreateImage`
### 2. Add stage config in image_flex_config.json
1. CloudFront distribution should be created before adding stage config
2. Designate the CloudFront `DistributionId` you want to link to the stage in `image_flex_config.json`
3. Add values for `CacheBehavior_1`
   
### 3. Update CloudFront Distribution
* update CloudFront Distribution with new CacheBehavior
  ```bash
  python3 manage_cloudfront_config.py dev update
  ```
* view CloudFront Distribution configuation
  ```bash
  python3 manage_cloudfront_config.py dev view
  ```
   
### Example
* `image_flex_config.json`
  ``` json
  {
      "dev": {
          "DistributionId": "E1Z2X3C4V5B6",
          "CacheBehavior_1": {
            "PathPattern": "*",
            "TargetOriginId": "example-project-dev.s3.ap-northeast-2.amazonaws.com",
            "TrustedSigners": {
                "Enabled": false,
                "Quantity": 0
            },
            "TrustedKeyGroups": {
                "Enabled": false,
                "Quantity": 0
            },
            "ViewerProtocolPolicy": "allow-all",
            "AllowedMethods": {
                "Quantity": 2,
                "Items": [
                    "HEAD",
                    "GET"
                ],
                "CachedMethods": {
                    "Quantity": 2,
                    "Items": [
                        "HEAD",
                        "GET"
                    ]
                }
            },
            "SmoothStreaming": false,
            "Compress": true,
            "LambdaFunctionAssociations": {
                "Quantity": 2,
                "Items": [
                    {
                        "LambdaFunctionARN": "arn:aws:lambda:us-east-1:123456789012:function:example-project-dev-UriToS3Key:1",
                        "EventType": "viewer-request",
                        "IncludeBody": true
                    },
                    {
                        "LambdaFunctionARN": "arn:aws:lambda:us-east-1:123456789012:function:example-project-dev-GetOrCreateImage:1",
                        "EventType": "origin-response",
                        "IncludeBody": false
                    }
                ]
            },
            "FunctionAssociations": {
                "Quantity": 0
            },
            "FieldLevelEncryptionId": "",
            "ForwardedValues": {
                "QueryString": true,
                "Cookies": {
                    "Forward": "none"
                },
                "Headers": {
                    "Quantity": 4,
                    "Items": [
                        "Origin",
                        "Access-Control-Request-Method",
                        "Access-Control-Allow-Origin",
                        "Access-Control-Request-Headers"
                    ]
                },
                "QueryStringCacheKeys": {
                    "Quantity": 2,
                    "Items": [
                        "h",
                        "w"
                    ]
                }
            },
            "MinTTL": 0,
            "DefaultTTL": 86400,
            "MaxTTL": 31536000
        }
      },
      "prod": {
          "DistributionId": "E1Z2X3C4V5B7",
          "CacheBehavior_1": {
              "PathPattern": "*",
              "TargetOriginId": "example-project-prod.s3.ap-northeast-2.amazonaws.com",
              ...
          }
      }
  }
  ```
