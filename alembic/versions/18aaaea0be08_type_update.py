"""type update

Revision ID: 18aaaea0be08
Revises: 
Create Date: 2020-08-21 15:19:06.496769

"""
import re

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '18aaaea0be08'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('listing', sa.Column('transaction_type', sa.String))
    connection = op.get_bind()
    # Select all existing names that need migrating.
    results = connection.execute("SELECT id, type FROM public.listing")
    # Iterate over all selected data tuples.
    for id, type in results:
        if not type.startswith("search:"):
            pass
        # Split the existing name into first and last.
        type, transaction = parse_transaction(type)
        # Update the new columns.
        connection.execute("""UPDATE public.listing
                                SET type = '{type}', transaction_type= '{transaction}'
                                WHERE id = {id};
                                """.format(type=type, id=id,
                                           transaction=transaction))


def downgrade():
    pass


def camel_case_split(identifier):
    matches = re.finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z]['
                          'a-z])|$)', identifier)
    return [m.group(0) for m in matches]


def parse_transaction(type_str: str):
    type_map = {"Apartment": "WOHNUNG", "House": "HAUS"}
    transaction_map = {"Rent": "MIETE", "Buy": "KAUF"}
    type_str = type_str.replace("search:", "")
    if type_str == "FlatShareRoom":
        return "ZIMMER", "MIETE"
    parsed = camel_case_split(type_str)
    return type_map[parsed[0]], transaction_map[parsed[1]]
