from troposphere import (  # pyright: ignore[reportMissingTypeStubs]
    kms,
    Ref,
    Sub,
    Template,
)


class DbKmsKey:
    key: kms.Key

    def __init__(self, t: Template):
        self.key = t.add_resource(
            kms.Key(
                "KMSCMK",
                DeletionPolicy="Retain",
                KeyPolicy={
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {
                                "AWS": Sub("arn:aws:iam::${AWS::AccountId}:root")
                            },
                            "Action": "kms:*",
                            "Resource": "*",
                        },
                        {
                            "Effect": "Allow",
                            "Principal": "*",
                            "Action": [
                                "kms:Encrypt",
                                "kms:Decrypt",
                                "kms:ReEncrypt*",
                                "kms:GenerateDataKey*",
                                "kms:CreateGrant",
                                "kms:ListGrants",
                                "kms:DescribeKey",
                            ],
                            "Resource": "*",
                            "Condition": {
                                "StringEquals": {
                                    "kms:CallerAccount": Ref("AWS::AccountId"),
                                    "kms:ViaService": Sub(
                                        "rds.${AWS::Region}.amazonaws.com"
                                    ),
                                }
                            },
                        },
                    ],
                },
            )
        )
