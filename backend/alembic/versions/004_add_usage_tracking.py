"""add usage tracking

Revision ID: 004
Revises: 003
Create Date: 2025-01-17

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Usage 테이블 생성
    op.create_table(
        'usage',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('papers_analyzed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('rag_queries', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('api_calls', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('month', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_usage_id', 'usage', ['id'])
    op.create_index('ix_usage_user_year_month', 'usage', ['user_id', 'year', 'month'], unique=True)

    # PlanLimit 테이블 생성
    op.create_table(
        'plan_limits',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('plan_name', sa.String(), nullable=False),
        sa.Column('papers_per_month', sa.Integer(), nullable=False),
        sa.Column('rag_queries_per_month', sa.Integer(), nullable=False),
        sa.Column('api_calls_per_day', sa.Integer(), nullable=False),
        sa.Column('max_file_size_mb', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('pdf_export', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('priority_support', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_plan_limits_id', 'plan_limits', ['id'])
    op.create_index('ix_plan_limits_plan_name', 'plan_limits', ['plan_name'], unique=True)

    # 기본 플랜 제한 데이터 삽입
    op.execute("""
        INSERT INTO plan_limits (plan_name, papers_per_month, rag_queries_per_month, api_calls_per_day, max_file_size_mb, pdf_export, priority_support)
        VALUES
            ('free', 10, 50, 100, 5, 0, 0),
            ('basic', 100, 500, 1000, 10, 1, 0),
            ('pro', -1, -1, 10000, 50, 1, 1)
    """)


def downgrade() -> None:
    op.drop_index('ix_plan_limits_plan_name', 'plan_limits')
    op.drop_index('ix_plan_limits_id', 'plan_limits')
    op.drop_table('plan_limits')

    op.drop_index('ix_usage_user_year_month', 'usage')
    op.drop_index('ix_usage_id', 'usage')
    op.drop_table('usage')
