"""add two factor auth

Revision ID: 009
Revises: 008
Create Date: 2024-01-16

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '009'
down_revision = '008'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 2단계 인증 테이블 생성
    op.create_table(
        'two_factor_auth',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('secret', sa.String(), nullable=False),
        sa.Column('is_enabled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('backup_codes', sa.String(), nullable=True),
        sa.Column('enabled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id'),
    )

    # 인덱스 생성
    op.create_index('ix_two_factor_auth_id', 'two_factor_auth', ['id'])
    op.create_index('ix_two_factor_auth_user_id', 'two_factor_auth', ['user_id'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_two_factor_auth_user_id', table_name='two_factor_auth')
    op.drop_index('ix_two_factor_auth_id', table_name='two_factor_auth')
    op.drop_table('two_factor_auth')
