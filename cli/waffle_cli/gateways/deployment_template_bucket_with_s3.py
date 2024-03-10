import os
from typing import Any
from boto3 import Session  # pyright: ignore[reportMissingTypeStubs]
from boto3.session import Config  # pyright: ignore[reportMissingTypeStubs]
from ..application_logic.gateway_interfaces.deployment_template_bucket import (
    DeploymentTemplateBucket,
)


class DeploymentTemplateBucketWithS3(DeploymentTemplateBucket):
    def _get_client(self, deployment_id: str, aws_region: str) -> Any:
        return Session(profile_name=deployment_id).client(  # type: ignore
            "s3", region_name=aws_region, config=Config(signature_version="s3v4")  # type: ignore
        )

    def _get_bucket(self, deployment_id: str, bucket_name: str, aws_region: str) -> Any:
        return (
            Session(profile_name=deployment_id)
            .resource("s3", region_name=aws_region)  # type: ignore
            .Bucket(bucket_name)
        )

    def create_bucket_if_not_exist(
        self, deployment_id: str, bucket_name: str, aws_region: str
    ) -> None:
        client = self._get_client(deployment_id, aws_region)

        params: dict[str, str] = {
            "ACL": "private",
            "Bucket": bucket_name,
            "ObjectOwnership": "BucketOwnerEnforced",
        }
        # NOTE: This is another AWS mindblowing innovation:
        # setting the default value breaks execution
        if aws_region != "us-east-1":
            params["CreateBucketConfiguration"] = {  # type: ignore
                "LocationConstraint": aws_region
            }
        try:
            client.create_bucket(**params)
        except client.exceptions.BucketAlreadyExists:
            pass
        except client.exceptions.BucketAlreadyOwnedByYou:
            pass
        else:
            client.put_public_access_block(
                Bucket=bucket_name,
                PublicAccessBlockConfiguration={
                    "BlockPublicAcls": True,
                    "IgnorePublicAcls": True,
                    "BlockPublicPolicy": True,
                    "RestrictPublicBuckets": True,
                },
            )

    def upload_file(
        self, deployment_id: str, bucket_name: str, aws_region: str, file_path: str
    ) -> None:
        s3_key: str = (
            f"{self.get_url_base(deployment_id)}/{os.path.basename(file_path)}"
        )
        with open(file_path, "rb") as data:
            self._get_bucket(
                deployment_id=deployment_id,
                bucket_name=bucket_name,
                aws_region=aws_region,
            ).upload_fileobj(data, s3_key)

    def upload_obj(
        self,
        deployment_id: str,
        bucket_name: str,
        aws_region: str,
        key: str,
        content: str,
    ) -> str:
        self._get_client(deployment_id=deployment_id, aws_region=aws_region).put_object(
            Body=content, Key=key, Bucket=bucket_name
        )
        return f"{self.get_url_base(bucket_name)}/{key}"

    def get_url_base(self, bucket_name: str) -> str:
        return f"https://s3.amazonaws.com/{bucket_name}"
