from troposphere import s3, Template  # pyright: ignore[reportMissingTypeStubs]


class ArtifactsBucket:
    artifacts_bucket: s3.Bucket

    def __init__(self, t: Template):
        self.artifacts_bucket = t.add_resource(
            s3.Bucket(
                "ArtifactsBucket",
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
                PublicAccessBlockConfiguration=s3.PublicAccessBlockConfiguration(
                    BlockPublicAcls=True,
                    BlockPublicPolicy=True,
                    IgnorePublicAcls=True,
                    RestrictPublicBuckets=True,
                ),
            )
        )
