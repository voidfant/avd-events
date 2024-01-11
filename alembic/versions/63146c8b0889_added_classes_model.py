"""added classes model

Revision ID: 63146c8b0889
Revises: 4875423302aa
Create Date: 2024-01-10 21:13:38.863810

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '63146c8b0889'
down_revision = '4875423302aa'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('classes',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('platform', sa.VARCHAR(length=4), nullable=False),
    sa.Column('quota', sa.SmallInteger(), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('weekdays', sa.VARCHAR(length=7), nullable=False),
    sa.Column('intervals', sa.VARCHAR(length=3), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_classes_id'), 'classes', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_classes_id'), table_name='classes')
    op.drop_table('classes')
    # ### end Alembic commands ###