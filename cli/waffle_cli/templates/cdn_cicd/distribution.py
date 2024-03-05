from troposphere import (  # pyright: ignore[reportMissingTypeStubs]
    GetAtt,
    If,
    Join,
    Ref,
    cloudfront,
    Template,
)
from .conditions import Conditions
from .parameters import Parameters
from .logging_bucket import LoggingBucket
from .web_bucket import WebBucket


class Distribution:
    distribution: cloudfront.Distribution

    def __init__(
        self,
        t: Template,
        c: Conditions,
        p: Parameters,
        lb: LoggingBucket,
        wb: WebBucket,
    ):
        self.distribution = t.add_resource(
            cloudfront.Distribution(
                "FrontendDistribution",
                DistributionConfig=cloudfront.DistributionConfig(
                    Aliases=[
                        If(
                            c.alt_full_domain_name_specified,
                            Ref(p.alt_full_domain_name),
                            Join(
                                "", [Ref(p.web_subdomain), ".", Ref(p.full_domain_name)]
                            ),
                        )
                    ],
                    DefaultCacheBehavior=cloudfront.DefaultCacheBehavior(
                        ForwardedValues=cloudfront.ForwardedValues(QueryString=True),
                        TargetOriginId=Join(
                            "",
                            [
                                Ref(p.deployment_id),
                                "-",
                                Ref(p.pipeline_id),
                                "-ui-origin",
                            ],
                        ),
                        ViewerProtocolPolicy="redirect-to-https",
                    ),
                    DefaultRootObject="index.html",
                    Enabled=True,
                    HttpVersion="http2",
                    Logging=cloudfront.Logging(Bucket=GetAtt(lb.bucket, "DomainName")),
                    Origins=[
                        cloudfront.Origin(
                            Id=Join(
                                "",
                                [
                                    Ref(p.deployment_id),
                                    "-",
                                    Ref(p.pipeline_id),
                                    "-ui-origin",
                                ],
                            ),
                            # DomainName=GetAtt(mwfBucket, "DomainName"),
                            # S3OriginConfig=cloudfront.S3OriginConfig()
                            DomainName=Join(
                                "",
                                [
                                    Ref(wb.bucket),
                                    ".s3-website.",
                                    Ref("AWS::Region"),
                                    ".amazonaws.com",
                                ],
                            ),
                            CustomOriginConfig=cloudfront.CustomOriginConfig(
                                OriginProtocolPolicy="http-only"
                            ),
                        )
                    ],
                    ViewerCertificate=cloudfront.ViewerCertificate(
                        AcmCertificateArn=If(
                            c.alt_full_domain_name_specified,
                            Ref(p.alt_certificate_arn),
                            Ref(p.generic_certificate_arn),
                        ),
                        SslSupportMethod="sni-only",
                        MinimumProtocolVersion="TLSv1.2_2018",
                    ),
                ),
            )
        )
