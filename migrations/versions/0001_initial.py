from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None


def upgrade() -> None:
    op.create_table("phones", sa.Column("phone_id", sa.Uuid(), primary_key=True), sa.Column("vendor", sa.String(64), nullable=False), sa.Column("vendor_id", sa.String(128), nullable=False, unique=True), sa.Column("status", sa.String(32), nullable=False), sa.Column("adb_status", sa.String(32), nullable=False), sa.Column("tags", sa.JSON(), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.create_index("ix_phones_vendor", "phones", ["vendor"])
    op.create_index("ix_phones_status", "phones", ["status"])
    op.create_table("jobs", sa.Column("job_id", sa.Uuid(), primary_key=True), sa.Column("operation", sa.String(32), nullable=False), sa.Column("status", sa.String(32), nullable=False), sa.Column("attempts", sa.Integer(), nullable=False), sa.Column("next_retry_at", sa.DateTime(timezone=True)), sa.Column("last_error", sa.Text()), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.create_index("ix_jobs_status", "jobs", ["status"])
    op.create_table("job_items", sa.Column("item_id", sa.Uuid(), primary_key=True), sa.Column("job_id", sa.Uuid(), nullable=False), sa.Column("phone_id", sa.Uuid(), nullable=False), sa.Column("status", sa.String(32), nullable=False), sa.Column("attempts", sa.Integer(), nullable=False), sa.Column("error", sa.JSON()))
    op.create_index("ix_job_items_job_id", "job_items", ["job_id"])
    op.create_index("ix_job_items_phone_id", "job_items", ["phone_id"])
    op.create_table("audit_events", sa.Column("event_id", sa.Uuid(), primary_key=True), sa.Column("action", sa.String(64), nullable=False), sa.Column("actor", sa.String(128), nullable=False), sa.Column("resource", sa.String(64), nullable=False), sa.Column("resource_id", sa.String(128), nullable=False), sa.Column("metadata_json", sa.JSON(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()))


def downgrade() -> None:
    op.drop_table("audit_events")
    op.drop_table("job_items")
    op.drop_table("jobs")
    op.drop_table("phones")
