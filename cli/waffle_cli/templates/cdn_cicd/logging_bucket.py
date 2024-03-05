from troposphere import s3, Template  # pyright: ignore[reportMissingTypeStubs]


class LoggingBucket:
    bucket: s3.Bucket

    def __init__(self, t: Template):
        self.bucket = t.add_resource(
            s3.Bucket(
                "LoggingBucket",
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
                OwnershipControls=s3.OwnershipControls(
                    Rules=[
                        s3.OwnershipControlsRule(ObjectOwnership="BucketOwnerPreferred")
                    ]
                ),
                PublicAccessBlockConfiguration=s3.PublicAccessBlockConfiguration(
                    BlockPublicAcls=True,
                    BlockPublicPolicy=True,
                    IgnorePublicAcls=True,
                    RestrictPublicBuckets=True,
                ),
            )
        )
