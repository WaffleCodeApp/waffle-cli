from troposphere import (  # pyright: ignore[reportMissingTypeStubs]
    GetAtt,
    Join,
    Ref,
    s3,
    Template,
)


class WebBucket:
    bucket: s3.Bucket

    def __init__(self, t: Template):
        self.bucket = t.add_resource(
            s3.Bucket(
                "WebBucket",
                PublicAccessBlockConfiguration=s3.PublicAccessBlockConfiguration(
                    BlockPublicAcls=False,
                    BlockPublicPolicy=False,
                    IgnorePublicAcls=False,
                    RestrictPublicBuckets=False,
                ),
                WebsiteConfiguration=s3.WebsiteConfiguration(
                    ErrorDocument="index.html", IndexDocument="index.html"
                ),
                VersioningConfiguration=s3.VersioningConfiguration(
                    Status="Enabled",
                ),
                DeletionPolicy="Retain",
                BucketEncryption=s3.BucketEncryption(
                    ServerSideEncryptionConfiguration=[
                        s3.ServerSideEncryptionRule(
                            ServerSideEncryptionByDefault=s3.ServerSideEncryptionByDefault(
                                SSEAlgorithm="AES256"
                            )
                        )
                    ]
                ),
            )
        )

        t.add_resource(
            s3.BucketPolicy(
                "WebBucketPolicy",
                Bucket=Ref(self.bucket),
                PolicyDocument={
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": "*",
                            "Action": "s3:GetObject",
                            "Resource": Join(
                                "",
                                [GetAtt(self.bucket, "Arn"), "/*"],
                            ),
                        }
                    ],
                },
            )
        )
