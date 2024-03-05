from troposphere import (  # pyright: ignore[reportMissingTypeStubs]
    GetAtt,
    Join,
    Ref,
    s3,
    Template,
)
from awacs.aws import Principal
from .artifacts_bucket import ArtifactsBucket
from .cicd_roles import CicdRoles


class ArtifactsBucketPolicy:
    def __init__(self, t: Template, ab: ArtifactsBucket, cr: CicdRoles):
        t.add_resource(
            s3.BucketPolicy(
                "CiCdArtifactsBucketPolicy",
                Bucket=Ref(ab.artifacts_bucket),
                PolicyDocument={
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": Principal(
                                "AWS",
                                [
                                    GetAtt(cr.codepipeline_role, "Arn"),
                                    GetAtt(cr.codebuild_role, "Arn"),
                                ],
                            ),
                            "Action": [
                                "s3:GetObject",
                                "s3:GetObjectVersion",
                                "s3:GetBucketVersioning",
                            ],
                            "Resource": [
                                Join(
                                    "",
                                    [
                                        "arn:aws:s3:::",
                                        Ref(ab.artifacts_bucket),
                                    ],
                                ),
                                Join(
                                    "",
                                    [
                                        "arn:aws:s3:::",
                                        Ref(ab.artifacts_bucket),
                                        "/*",
                                    ],
                                ),
                            ],
                            "Condition": {"Bool": {"aws:SecureTransport": False}},
                        },
                        {
                            "Effect": "Allow",
                            "Principal": Principal(
                                "AWS",
                                [
                                    GetAtt(cr.codepipeline_role, "Arn"),
                                    GetAtt(cr.codebuild_role, "Arn"),
                                ],
                            ),
                            "Action": "s3:PutObject",
                            "Resource": [
                                Join(
                                    "",
                                    [
                                        "arn:aws:s3:::",
                                        Ref(ab.artifacts_bucket),
                                    ],
                                ),
                                Join(
                                    "",
                                    [
                                        "arn:aws:s3:::",
                                        Ref(ab.artifacts_bucket),
                                        "/*",
                                    ],
                                ),
                            ],
                        },
                    ],
                },
            )
        )
