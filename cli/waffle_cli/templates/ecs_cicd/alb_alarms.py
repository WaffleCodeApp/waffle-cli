from troposphere import (  # pyright: ignore[reportMissingTypeStubs]
    cloudwatch,
    GetAtt,
    If,
    ImportValue,
    Join,
    Ref,
    Template,
)
from .parameters import Parameters
from .conditions import Conditions
from .alb import Alb


class AlbAlarms:
    def __init__(self, t: Template, p: Parameters, c: Conditions, alb: Alb):
        t.add_resource(
            cloudwatch.Alarm(
                "AlbAlarm",
                ActionsEnabled=True,
                AlarmActions=[
                    If(
                        c.custom_alerts_sns_ref,
                        Ref(p.alerts_sns_ref),
                        ImportValue(
                            Join("", [Ref(p.deployment_id), "-AlertsSnsTopicRef"])
                        ),
                    )
                ],
                AlarmDescription="ALB server error > 0",
                Namespace="AWS/ApplicationELB",
                ComparisonOperator="GreaterThanThreshold",
                Threshold="0",
                Dimensions=[
                    cloudwatch.MetricDimension(
                        Name="LoadBalancer",
                        Value=GetAtt(alb.alb, "LoadBalancerFullName"),
                    )
                ],
                # Fire at the first occassion
                EvaluationPeriods=1,
                MetricName="HTTPCode_ELB_5XX_Count",
                Period=60,
                Statistic="Sum",
            )
        )

        t.add_resource(
            cloudwatch.Alarm(
                "AlbAlarm2",
                ActionsEnabled=True,
                AlarmActions=[
                    If(
                        c.custom_alerts_sns_ref,
                        Ref(p.alerts_sns_ref),
                        ImportValue(
                            Join("", [Ref(p.deployment_id), "-AlertsSnsTopicRef"])
                        ),
                    )
                ],
                AlarmDescription="ALB unhealthy instances > 0",
                Namespace="AWS/ApplicationELB",
                ComparisonOperator="GreaterThanThreshold",
                Threshold="0",
                Dimensions=[
                    cloudwatch.MetricDimension(
                        Name="LoadBalancer",
                        Value=GetAtt(alb.alb, "LoadBalancerFullName"),
                    )
                ],
                # Fire at the first occassion
                EvaluationPeriods=1,
                MetricName="UnHealthyHostCount",
                Period=60,
                Statistic="Sum",
            )
        )

        t.add_resource(
            cloudwatch.Alarm(
                "AlbAlarm3",
                ActionsEnabled=True,
                AlarmActions=[
                    If(
                        c.custom_alerts_sns_ref,
                        Ref(p.alerts_sns_ref),
                        ImportValue(
                            Join("", [Ref(p.deployment_id), "-AlertsSnsTopicRef"])
                        ),
                    )
                ],
                AlarmDescription="ALB average latency > 3 s",
                Namespace="AWS/ApplicationELB",
                # TODO: best practice is average
                # https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-cloudwatch-metrics.html
                ComparisonOperator="GreaterThanThreshold",
                Threshold="3",
                Dimensions=[
                    cloudwatch.MetricDimension(
                        Name="LoadBalancer",
                        Value=GetAtt(alb.alb, "LoadBalancerFullName"),
                    )
                ],
                # Fire if happens twice in a row
                EvaluationPeriods=2,
                MetricName="TargetResponseTime",
                Period=60,
                Statistic="Average",
            )
        )
