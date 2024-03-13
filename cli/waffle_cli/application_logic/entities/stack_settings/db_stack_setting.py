from .stack_setting import StackSetting


class DbStackSetting(StackSetting):
    database_id: str
    allocated_storage_size: str | None = None
    db_type: str | None = None
    family: str | None = None
    postgres_engine_version: str | None = None
    instance_class: str | None = None
    create_replica: str | None = None
