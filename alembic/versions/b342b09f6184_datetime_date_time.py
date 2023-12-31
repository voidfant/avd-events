"""-datetime +date +time

Revision ID: b342b09f6184
Revises: 48385f4fedd4
Create Date: 2023-12-17 20:49:33.654482

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'b342b09f6184'
down_revision = '48385f4fedd4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('applications', 'platform',
               existing_type=sa.SMALLINT(),
               type_=sa.VARCHAR(length=4),
               existing_nullable=False)
    op.add_column('events', sa.Column('time', sa.Time(), nullable=False))
    op.add_column('events', sa.Column('date', sa.Date(), nullable=False))
    op.drop_column('events', 'timestamp')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('events', sa.Column('timestamp', postgresql.TIMESTAMP(), autoincrement=False, nullable=False))
    op.drop_column('events', 'date')
    op.drop_column('events', 'time')
    op.alter_column('applications', 'platform',
               existing_type=sa.VARCHAR(length=4),
               type_=sa.SMALLINT(),
               existing_nullable=False)
    # ### end Alembic commands ###
