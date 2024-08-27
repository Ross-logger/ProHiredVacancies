"""Database creation

Revision ID: 87bfd75fbedb
Revises: 
Create Date: 2024-08-24 14:04:35.027953

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '87bfd75fbedb'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the vacancy table
    op.create_table(
        'vacancy',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('title', sa.String, nullable=False),
        sa.Column('salary', sa.String, nullable=False),
        sa.Column('description', sa.String, nullable=True),
        sa.Column('user_id', sa.Integer, nullable=False)
    )


def downgrade() -> None:
    # Drop the vacancy table
    op.drop_table('vacancy')
