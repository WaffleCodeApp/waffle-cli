from troposphere import (  # pyright: ignore[reportMissingTypeStubs]
    cloudwatch,
    If,
    ImportValue,
    Join,
    rds,
    Ref,
    Template,
)

from .parameters import Parameters
from .conditions import Conditions
from .aurora_cluster import AuroraCluster
from .rds_instances import RdsInstances
from .db_parameter_group import DbParameterGroup


class Alarms:
    def __init__(
        self,
        t: Template,
        p: Parameters,
        c: Conditions,
        ac: AuroraCluster,
        ri: RdsInstances,
        dbpg: DbParameterGroup,
    ):
        t.add_resource(
            cloudwatch.Alarm(
                "CPUUtilizationAlarm",
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
                AlarmDescription="DB CPU utilization high",
                Dimensions=[
                    cloudwatch.MetricDimension(
                        Name="First instance",
                        Value=If(
                            c.aurora_selected,
                            Ref(ac.first_instance),
                            Ref(ri.first_instance),
                        ),
                    ),
                    If(
                        c.aurora_selected,
                        cloudwatch.MetricDimension(
                            Name="Second instance",
                            Value=Ref(ac.second_instance),
                        ),
                        If(
                            c.create_replica,
                            cloudwatch.MetricDimension(
                                Name="Second instance",
                                Value=Ref(ri.second_instance),
                            ),
                            Ref("AWS::NoValue"),
                        ),
                    ),
                ],
                MetricName="CPUUtilization",
                Statistic="Maximum",
                Namespace="AWS/RDS",
                Threshold="80",
                Unit="Percent",
                ComparisonOperator="GreaterThanOrEqualToThreshold",
                # Fire if goes on for at least 5 minutes
                Period=60,
                EvaluationPeriods=5,
                TreatMissingData="notBreaching",
            )
        )

        t.add_resource(
            cloudwatch.Alarm(
                "MaxUsedTxIDsAlarm",
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
                AlarmDescription="DB maximum used transaction IDs high",
                Dimensions=[
                    cloudwatch.MetricDimension(
                        Name="First instance",
                        Value=If(
                            c.aurora_selected,
                            Ref(ac.first_instance),
                            Ref(ri.first_instance),
                        ),
                    ),
                    If(
                        c.aurora_selected,
                        cloudwatch.MetricDimension(
                            Name="Second instance",
                            Value=Ref(ac.second_instance),
                        ),
                        If(
                            c.create_replica,
                            cloudwatch.MetricDimension(
                                Name="Second instance",
                                Value=Ref(ri.second_instance),
                            ),
                            Ref("AWS::NoValue"),
                        ),
                    ),
                ],
                MetricName="MaximumUsedTransactionIDs",
                Statistic="Average",
                Namespace="AWS/RDS",
                # A PostgreSQL database can have two billion “in-flight” unvacuumed transactions
                Threshold="600000000",
                Unit="Count",
                ComparisonOperator="GreaterThanOrEqualToThreshold",
                # Fire if goes on for at least 5 minutes
                Period=60,
                EvaluationPeriods=5,
                TreatMissingData="notBreaching",
            )
        )

        t.add_resource(
            cloudwatch.Alarm(
                "FreeLocalStorageAlarm",
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
                AlarmDescription="DB free local storage low",
                Dimensions=[
                    cloudwatch.MetricDimension(
                        Name="First instance",
                        Value=If(
                            c.aurora_selected,
                            Ref(ac.first_instance),
                            Ref(ri.first_instance),
                        ),
                    ),
                    If(
                        c.aurora_selected,
                        cloudwatch.MetricDimension(
                            Name="Second instance",
                            Value=Ref(ac.second_instance),
                        ),
                        If(
                            c.create_replica,
                            cloudwatch.MetricDimension(
                                Name="Second instance",
                                Value=Ref(ri.second_instance),
                            ),
                            Ref("AWS::NoValue"),
                        ),
                    ),
                ],
                MetricName="FreeLocalStorage",
                Statistic="Average",
                Namespace="AWS/RDS",
                Threshold="5368709120",
                Unit="Bytes",
                ComparisonOperator="LessThanOrEqualToThreshold",
                # Fire for the first occassion
                Period=60,
                EvaluationPeriods=1,
                TreatMissingData="notBreaching",
            )
        )

        t.add_resource(
            cloudwatch.Alarm(
                "FreeableMemoryAlarm",
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
                AlarmDescription="DB freeable memory low",
                Dimensions=[
                    cloudwatch.MetricDimension(
                        Name="First instance",
                        Value=If(
                            c.aurora_selected,
                            Ref(ac.first_instance),
                            Ref(ri.first_instance),
                        ),
                    ),
                    If(
                        c.aurora_selected,
                        cloudwatch.MetricDimension(
                            Name="Second instance",
                            Value=Ref(ac.second_instance),
                        ),
                        If(
                            c.create_replica,
                            cloudwatch.MetricDimension(
                                Name="Second instance",
                                Value=Ref(ri.second_instance),
                            ),
                            Ref("AWS::NoValue"),
                        ),
                    ),
                ],
                MetricName="FreeableMemory",
                Statistic="Average",
                Namespace="AWS/RDS",
                Threshold="10485760",
                Unit="Bytes",
                ComparisonOperator="LessThanOrEqualToThreshold",
                # Fire for the first occassion
                Period=60,
                EvaluationPeriods=1,
                TreatMissingData="notBreaching",
            )
        )

        t.add_resource(
            rds.EventSubscription(
                "AuroraClusterEventSubscription",
                Condition=c.aurora_selected,
                EventCategories=["failover", "failure", "notification"],
                SnsTopicArn=If(
                    c.custom_alerts_sns_ref,
                    Ref(p.alerts_sns_ref),
                    ImportValue(Join("", [Ref(p.deployment_id), "-AlertsSnsTopicRef"])),
                ),
                SourceIds=[
                    If(
                        c.aurora_selected,
                        Ref(ac.cluster),
                        Ref("AWS::NoValue"),
                    )
                ],
                SourceType="db-cluster",
            )
        )

        t.add_resource(
            rds.EventSubscription(
                "InstanceEventSubscription",
                EventCategories=[
                    "availability",
                    "configuration change",
                    "deletion",
                    "failover",
                    "failure",
                    "maintenance",
                    "notification",
                    "recovery",
                ],
                SnsTopicArn=If(
                    c.custom_alerts_sns_ref,
                    Ref(p.alerts_sns_ref),
                    ImportValue(Join("", [Ref(p.deployment_id), "-AlertsSnsTopicRef"])),
                ),
                SourceIds=[
                    If(
                        c.aurora_selected,
                        Ref(ac.first_instance),
                        Ref(ri.first_instance),
                    ),
                    If(
                        c.aurora_selected,
                        Ref(ac.second_instance),
                        If(
                            c.create_replica,
                            Ref(ri.second_instance),
                            Ref("AWS::NoValue"),
                        ),
                    ),
                ],
                SourceType="db-instance",
            )
        )

        t.add_resource(
            rds.EventSubscription(
                "DBParameterGroupEventSubscription",
                Condition=c.aurora_selected,
                EventCategories=["configuration change"],
                SnsTopicArn=If(
                    c.custom_alerts_sns_ref,
                    Ref(p.alerts_sns_ref),
                    ImportValue(Join("", [Ref(p.deployment_id), "-AlertsSnsTopicRef"])),
                ),
                SourceIds=[
                    If(
                        c.aurora_selected,
                        Ref(dbpg.group),
                        Ref("AWS::NoValue"),
                    )
                ],
                SourceType="db-parameter-group",
            )
        )
