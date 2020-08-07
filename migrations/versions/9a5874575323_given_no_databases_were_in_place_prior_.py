"""Given no databases were in place prior to this. I'm wiping the db history out and starting over.

Revision ID: 9a5874575323
Revises: 
Create Date: 2020-08-06 21:23:49.054710

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9a5874575323'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('regions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('name_label', sa.String(), nullable=True),
    sa.Column('name_abbr', sa.String(), nullable=True),
    sa.Column('county_number', sa.String(), nullable=True),
    sa.Column('fips', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('subscribers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('phone_number', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('phone_number')
    )
    op.create_table('entries',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date', sa.Date(), nullable=True),
    sa.Column('total', sa.Integer(), nullable=True),
    sa.Column('f_0_9', sa.Integer(), nullable=True),
    sa.Column('m_0_9', sa.Integer(), nullable=True),
    sa.Column('t_0_9', sa.Integer(), nullable=True),
    sa.Column('f_10_19', sa.Integer(), nullable=True),
    sa.Column('m_10_19', sa.Integer(), nullable=True),
    sa.Column('t_10_19', sa.Integer(), nullable=True),
    sa.Column('f_20_29', sa.Integer(), nullable=True),
    sa.Column('m_20_29', sa.Integer(), nullable=True),
    sa.Column('t_20_29', sa.Integer(), nullable=True),
    sa.Column('f_30_39', sa.Integer(), nullable=True),
    sa.Column('m_30_39', sa.Integer(), nullable=True),
    sa.Column('t_30_39', sa.Integer(), nullable=True),
    sa.Column('f_40_49', sa.Integer(), nullable=True),
    sa.Column('m_40_49', sa.Integer(), nullable=True),
    sa.Column('t_40_49', sa.Integer(), nullable=True),
    sa.Column('f_50_59', sa.Integer(), nullable=True),
    sa.Column('m_50_59', sa.Integer(), nullable=True),
    sa.Column('t_50_59', sa.Integer(), nullable=True),
    sa.Column('f_60_69', sa.Integer(), nullable=True),
    sa.Column('m_60_69', sa.Integer(), nullable=True),
    sa.Column('t_60_69', sa.Integer(), nullable=True),
    sa.Column('f_70_79', sa.Integer(), nullable=True),
    sa.Column('m_70_79', sa.Integer(), nullable=True),
    sa.Column('t_70_79', sa.Integer(), nullable=True),
    sa.Column('f_80_89', sa.Integer(), nullable=True),
    sa.Column('m_80_89', sa.Integer(), nullable=True),
    sa.Column('t_80_89', sa.Integer(), nullable=True),
    sa.Column('f_90_99', sa.Integer(), nullable=True),
    sa.Column('m_90_99', sa.Integer(), nullable=True),
    sa.Column('t_90_99', sa.Integer(), nullable=True),
    sa.Column('f_100', sa.Integer(), nullable=True),
    sa.Column('m_100', sa.Integer(), nullable=True),
    sa.Column('t_100', sa.Integer(), nullable=True),
    sa.Column('notes', sa.String(), nullable=True),
    sa.Column('new_case', sa.Integer(), nullable=True),
    sa.Column('total_deaths', sa.Integer(), nullable=True),
    sa.Column('hospitalization_count', sa.Integer(), nullable=True),
    sa.Column('total_recovered', sa.Integer(), nullable=True),
    sa.Column('total_active', sa.Integer(), nullable=True),
    sa.Column('region_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['region_id'], ['regions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('subscriptions',
    sa.Column('subscriber_id', sa.Integer(), nullable=False),
    sa.Column('region_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['region_id'], ['regions.id'], ),
    sa.ForeignKeyConstraint(['subscriber_id'], ['subscribers.id'], ),
    sa.PrimaryKeyConstraint('subscriber_id', 'region_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('subscriptions')
    op.drop_table('entries')
    op.drop_table('subscribers')
    op.drop_table('regions')
    # ### end Alembic commands ###
