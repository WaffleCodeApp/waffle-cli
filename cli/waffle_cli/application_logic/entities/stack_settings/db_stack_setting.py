from pydantic import BaseModel


class DbStackSetting(BaseModel):
    database_id: str
    allocated_storage_size: str | None = None
    db_type: str | None = None
    family: str | None = None
    postgres_engine_version: str | None = None
    instance_class: str | None = None
    create_replica: str | None = None

    def get_stack_id(self):
        return f"db|{self.database_id}"
