"""add indexes for performance

Revision ID: 002
Revises: 001
Create Date: 2024-01-15

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Users 테이블 인덱스
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_username', 'users', ['username'])
    op.create_index('ix_users_is_active', 'users', ['is_active'])
    op.create_index('ix_users_created_at', 'users', ['created_at'])

    # Papers 테이블 인덱스
    op.create_index('ix_papers_user_id', 'papers', ['user_id'])
    op.create_index('ix_papers_pubmed_id', 'papers', ['pubmed_id'])
    op.create_index('ix_papers_doi', 'papers', ['doi'])
    op.create_index('ix_papers_source', 'papers', ['source'])
    op.create_index('ix_papers_created_at', 'papers', ['created_at'])
    op.create_index('ix_papers_publication_date', 'papers', ['publication_date'])
    # 복합 인덱스: 사용자별 최신 논문 조회 최적화
    op.create_index('ix_papers_user_created', 'papers', ['user_id', 'created_at'])

    # Analyses 테이블 인덱스
    op.create_index('ix_analyses_user_id', 'analyses', ['user_id'])
    op.create_index('ix_analyses_paper_id', 'analyses', ['paper_id'])
    op.create_index('ix_analyses_analysis_type', 'analyses', ['analysis_type'])
    op.create_index('ix_analyses_created_at', 'analyses', ['created_at'])
    # 복합 인덱스: 사용자별 분석 유형 조회 최적화
    op.create_index('ix_analyses_user_type', 'analyses', ['user_id', 'analysis_type'])
    op.create_index('ix_analyses_user_created', 'analyses', ['user_id', 'created_at'])

    # Subscriptions 테이블 인덱스
    op.create_index('ix_subscriptions_user_id', 'subscriptions', ['user_id'])
    op.create_index('ix_subscriptions_plan_id', 'subscriptions', ['plan_id'])
    op.create_index('ix_subscriptions_status', 'subscriptions', ['status'])
    op.create_index('ix_subscriptions_stripe_id', 'subscriptions', ['stripe_subscription_id'])
    op.create_index('ix_subscriptions_start_date', 'subscriptions', ['start_date'])
    op.create_index('ix_subscriptions_end_date', 'subscriptions', ['end_date'])
    # 복합 인덱스: 활성 구독 조회 최적화
    op.create_index('ix_subscriptions_user_status', 'subscriptions', ['user_id', 'status'])

    # Subscription Plans 테이블 인덱스
    op.create_index('ix_subscription_plans_name', 'subscription_plans', ['name'])
    op.create_index('ix_subscription_plans_stripe_id', 'subscription_plans', ['stripe_price_id'])


def downgrade() -> None:
    # Subscription Plans 인덱스 삭제
    op.drop_index('ix_subscription_plans_stripe_id', table_name='subscription_plans')
    op.drop_index('ix_subscription_plans_name', table_name='subscription_plans')

    # Subscriptions 인덱스 삭제
    op.drop_index('ix_subscriptions_user_status', table_name='subscriptions')
    op.drop_index('ix_subscriptions_end_date', table_name='subscriptions')
    op.drop_index('ix_subscriptions_start_date', table_name='subscriptions')
    op.drop_index('ix_subscriptions_stripe_id', table_name='subscriptions')
    op.drop_index('ix_subscriptions_status', table_name='subscriptions')
    op.drop_index('ix_subscriptions_plan_id', table_name='subscriptions')
    op.drop_index('ix_subscriptions_user_id', table_name='subscriptions')

    # Analyses 인덱스 삭제
    op.drop_index('ix_analyses_user_created', table_name='analyses')
    op.drop_index('ix_analyses_user_type', table_name='analyses')
    op.drop_index('ix_analyses_created_at', table_name='analyses')
    op.drop_index('ix_analyses_analysis_type', table_name='analyses')
    op.drop_index('ix_analyses_paper_id', table_name='analyses')
    op.drop_index('ix_analyses_user_id', table_name='analyses')

    # Papers 인덱스 삭제
    op.drop_index('ix_papers_user_created', table_name='papers')
    op.drop_index('ix_papers_publication_date', table_name='papers')
    op.drop_index('ix_papers_created_at', table_name='papers')
    op.drop_index('ix_papers_source', table_name='papers')
    op.drop_index('ix_papers_doi', table_name='papers')
    op.drop_index('ix_papers_pubmed_id', table_name='papers')
    op.drop_index('ix_papers_user_id', table_name='papers')

    # Users 인덱스 삭제
    op.drop_index('ix_users_created_at', table_name='users')
    op.drop_index('ix_users_is_active', table_name='users')
    op.drop_index('ix_users_username', table_name='users')
    op.drop_index('ix_users_email', table_name='users')
