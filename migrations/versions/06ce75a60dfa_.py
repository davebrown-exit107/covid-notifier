"""empty message

Revision ID: 06ce75a60dfa
Revises: 85c63fc94e54
Create Date: 2020-07-25 11:45:50.356714

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '06ce75a60dfa'
down_revision = '85c63fc94e54'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'subscribers', ['phone_number'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'subscribers', type_='unique')
    # ### end Alembic commands ###