"""create_template_prompt

Revision ID: 054_create_template_prompt
Revises: 5755c0b95839
Create Date: 2025-01-XX XX:XX:XX.XXXXXX

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '054_create_template_prompt'
down_revision = '5755c0b95839'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'template_prompt',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('oid', sa.BigInteger(), nullable=True),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('datasource_id', sa.BigInteger(), nullable=True),
        sa.Column('enabled', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('create_time', sa.DateTime(timezone=False), nullable=True),
        sa.Column('update_time', sa.DateTime(timezone=False), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_template_prompt_id'), 'template_prompt', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    op.drop_index(op.f('ix_template_prompt_id'), table_name='template_prompt')
    op.drop_table('template_prompt')
    # ### end Alembic commands ###

