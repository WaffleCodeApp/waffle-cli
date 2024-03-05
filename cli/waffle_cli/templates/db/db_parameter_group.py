from troposphere import rds, Ref, Template  # pyright: ignore[reportMissingTypeStubs]

from .conditions import Conditions
from .parameters import Parameters


class DbParameterGroup:
    group: rds.DBParameterGroup

    def __init__(self, t: Template, p: Parameters, c: Conditions):
        self.group = t.add_resource(
            rds.DBParameterGroup(
                "DBParamGroup",
                Description="DB Instance Parameter Group",
                Family=Ref(p.family),
                Parameters={
                    "shared_preload_libraries": "auto_explain,pg_stat_statements,"
                    "pg_hint_plan,pgaudit",
                    "log_statement": "ddl",
                    "log_connections": 1,
                    "log_disconnections": 1,
                    "log_lock_waits": 1,
                    "log_min_duration_statement": 5000,
                    "auto_explain.log_min_duration": 5000,
                    "auto_explain.log_verbose": 1,
                    "log_rotation_age": 1440,
                    "log_rotation_size": 102400,
                    "rds.log_retention_period": 10080,
                    "random_page_cost": 1,
                    "track_activity_query_size": 16384,
                    "idle_in_transaction_session_timeout": 7200000,
                    "statement_timeout": 7200000,
                    "search_path": '"$user",public',
                    "max_standby_streaming_delay": 180000,
                },
            )
        )
