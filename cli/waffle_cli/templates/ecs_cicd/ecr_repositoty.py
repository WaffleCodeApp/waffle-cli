from troposphere import (  # pyright: ignore[reportMissingTypeStubs]
    ecr,
    GetAtt,
    Join,
    Ref,
    Template,
)
from awacs.aws import Action, Allow, Statement, Principal, Policy

from .cicd_roles import CicdRoles


class EcrRepositoty:
    repository: ecr.Repository
    uri: Join

    def __init__(self, t: Template, cr: CicdRoles):
        self.repository = t.add_resource(
            ecr.Repository(
                "Repo",
                # DeletionPolicy="Retain",  # TODO
                # NOTE repository names can't handle upper chase
                # characters, and there's no way to convert them
                # from CloudFormation
                RepositoryName=Ref("AWS::NoValue"),
                RepositoryPolicyText=Policy(
                    Version="2008-10-17",
                    Statement=[
                        Statement(
                            Effect=Allow,
                            Principal=Principal(
                                "AWS",
                                [
                                    GetAtt(cr.codepipeline_role, "Arn"),
                                    GetAtt(cr.codebuild_role, "Arn"),
                                ],
                            ),
                            Action=[
                                Action("ecr", "GetDownloadUrlForLayer"),
                                Action("ecr", "BatchGetImage"),
                                Action("ecr", "BatchCheckLayerAvailability"),
                                Action("ecr", "PutImage"),
                                Action("ecr", "InitiateLayerUpload"),
                                Action("ecr", "UploadLayerPart"),
                                Action("ecr", "CompleteLayerUpload"),
                                Action("ecr", "GetAuthorizationToken"),
                            ],
                        )
                    ],
                ),
            )
        )

        self.uri = Join(
            "",
            [
                Ref("AWS::AccountId"),
                ".dkr.ecr.",
                Ref("AWS::Region"),
                ".amazonaws.com/",
                Ref(self.repository),
            ],
        )
