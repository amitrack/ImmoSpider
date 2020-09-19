"""Added view to aggregate the results of each crawler

Revision ID: e143f8097f58
Revises: 941056515120
Create Date: 2020-09-19 11:39:12.380438

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
from sqlalchemy import engine_from_config
from sqlalchemy.engine import reflection

revision = 'e143f8097f58'
down_revision = '941056515120'
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
    connection = op.get_bind()
    connection.execute("""CREATE OR REPLACE VIEW all_listings as
SELECT immo_id as source_id, url, title address, zip_code, city, district,
NULL as country, NULL as broker_url, contact_name as broker, sqm as living_area,
area, rooms, price, "type", transaction_type, first_found,
found_last, crawl_id, 'immobilienscout24.de' as "source" from public.listing 
union 
SELECT immowelt_id as source_id, url, title address, zip_code, city, district,
country, broker, broker_url, living_area, area, rooms, price, "type",
transaction_type, first_found, found_last, crawl_id,
'immowelt.de' as "source" from public.immowelt_listings
union 
SELECT crozilla_id as source_id, url, title address, zip_code, city, district,
country, broker, broker_url, living_area, area, rooms, price, "type",
transaction_type, first_found, found_last, crawl_id,
'crozilla.com' as "source" from public.crozilla_listings""")


def downgrade():
    connection = op.get_bind()
    connection.execute("DROP VIEW all_listings")
