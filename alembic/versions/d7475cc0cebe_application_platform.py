"""application -platform

Revision ID: d7475cc0cebe
Revises: cb4f33df8c12
Create Date: 2023-12-18 17:51:22.355395

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd7475cc0cebe'
down_revision = 'cb4f33df8c12'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('applications', 'platform')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('applications', sa.Column('platform', sa.VARCHAR(length=4), autoincrement=False, nullable=False))
    # ### end Alembic commands ###
