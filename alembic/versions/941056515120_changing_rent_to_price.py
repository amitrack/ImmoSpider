"""Changing rent to price

Revision ID: 941056515120
Revises: 18aaaea0be08
Create Date: 2020-08-24 11:11:56.092367

"""
from alembic import op

# revision identifiers, used by Alembic.
from sqlalchemy import engine_from_config
from sqlalchemy.engine import reflection


revision = '941056515120'
down_revision = '18aaaea0be08'
branch_labels = None
depends_on = None

def table_has_column(table, column):
    config = op.get_context().config
    engine = engine_from_config(
        config.get_section(config.config_ini_section), prefix='sqlalchemy.')
    insp = reflection.Inspector.from_engine(engine)
    has_column = False
    for col in insp.get_columns(table):
        if column not in col['name']:
            continue
        has_column = True
    return has_column


def upgrade():
    if table_has_column("listing","price"):
        return
    connection = op.get_bind()
    connection.execute("ALTER TABLE public.listing RENAME COLUMN rent TO price")


def downgrade():
    connection = op.get_bind()
    connection.execute("ALTER TABLE public.listing RENAME COLUMN price TO rent")
