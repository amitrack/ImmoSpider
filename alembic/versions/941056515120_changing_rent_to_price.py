"""Changing rent to price

Revision ID: 941056515120
Revises: 18aaaea0be08
Create Date: 2020-08-24 11:11:56.092367

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '941056515120'
down_revision = '18aaaea0be08'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute("ALTER TABLE public.listing RENAME COLUMN rent TO price")


def downgrade():
    connection = op.get_bind()
    connection.execute("ALTER TABLE public.listing RENAME COLUMN price TO rent")
