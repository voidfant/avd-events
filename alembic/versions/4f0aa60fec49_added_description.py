"""added description

Revision ID: 4f0aa60fec49
Revises: 71cbaf45ebb8
Create Date: 2023-12-10 18:55:15.957568

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4f0aa60fec49'
down_revision = '71cbaf45ebb8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('events', sa.Column('description', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('events', 'description')
    # ### end Alembic commands ###