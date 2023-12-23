"""initial

Revision ID: 71cbaf45ebb8
Revises: 
Create Date: 2023-12-10 18:47:34.938362

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '71cbaf45ebb8'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('events',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('platform', sa.SmallInteger(), nullable=False),
    sa.Column('quota', sa.SmallInteger(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_events_id'), 'events', ['id'], unique=False)
    op.create_table('users',
    sa.Column('id', sa.String(), autoincrement=False, nullable=False),
    sa.Column('role', sa.Boolean(), server_default="false", nullable=True),
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_table('applications',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('event_id', sa.Integer(), nullable=True),
    sa.Column('applicant_id', sa.String(), nullable=True),
    sa.Column('platform', sa.SmallInteger(), nullable=False),
    sa.Column('guests_amount', sa.SmallInteger(), nullable=False),
    sa.Column('confirmed', sa.Boolean(), server_default='false', nullable=True),
    sa.ForeignKeyConstraint(['applicant_id'], ['users.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_applications_id'), 'applications', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_applications_id'), table_name='applications')
    op.drop_table('applications')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_events_id'), table_name='events')
    op.drop_table('events')
    # ### end Alembic commands ###
