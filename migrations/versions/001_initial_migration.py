"""Initial migration - Create all tables

Revision ID: 001
Revises: 
Create Date: 2025-10-15

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Table market_data
    op.create_table('market_data',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=True),
        sa.Column('type', sa.String(length=20), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('base_currency', sa.String(length=10), nullable=True),
        sa.Column('quote_currency', sa.String(length=10), nullable=True),
        sa.Column('is_active', sa.Integer(), nullable=False),
        sa.Column('last_updated', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('symbol')
    )
    op.create_index('ix_market_data_symbol', 'market_data', ['symbol'], unique=False)

    # Table price_history
    op.create_table('price_history',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('interval', sa.String(length=10), nullable=False),
        sa.Column('open_price', sa.Float(), nullable=False),
        sa.Column('high_price', sa.Float(), nullable=False),
        sa.Column('low_price', sa.Float(), nullable=False),
        sa.Column('close_price', sa.Float(), nullable=False),
        sa.Column('volume', sa.Float(), nullable=True),
        sa.Column('market_timestamp', sa.DateTime(), nullable=False),
        sa.Column('data_quality', sa.String(length=20), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_price_history_symbol', 'price_history', ['symbol'], unique=False)
    op.create_index('ix_price_history_market_timestamp', 'price_history', ['market_timestamp'], unique=False)

    # Table alerts
    op.create_table('alerts',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=True),
        sa.Column('provider', sa.String(length=50), nullable=True),
        sa.Column('is_read', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Integer(), nullable=False),
        sa.Column('priority', sa.String(length=20), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_alerts_symbol', 'alerts', ['symbol'], unique=False)

    # Table price_alerts
    op.create_table('price_alerts',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('condition_type', sa.String(length=20), nullable=False),
        sa.Column('target_price', sa.Float(), nullable=True),
        sa.Column('target_price_min', sa.Float(), nullable=True),
        sa.Column('target_price_max', sa.Float(), nullable=True),
        sa.Column('change_percent', sa.Float(), nullable=True),
        sa.Column('is_active', sa.Integer(), nullable=False),
        sa.Column('is_triggered', sa.Integer(), nullable=False),
        sa.Column('triggered_at', sa.DateTime(), nullable=True),
        sa.Column('name', sa.String(length=100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('notification_method', sa.String(length=50), nullable=True),
        sa.Column('reference_price', sa.Float(), nullable=True),
        sa.Column('reference_timestamp', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_price_alerts_symbol', 'price_alerts', ['symbol'], unique=False)

    # Table news_articles
    op.create_table('news_articles',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('url', sa.String(length=1000), nullable=False),
        sa.Column('source', sa.String(length=100), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('author', sa.String(length=200), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('tags', sa.String(length=500), nullable=True),
        sa.Column('symbols', sa.String(length=500), nullable=True),
        sa.Column('published_at', sa.DateTime(), nullable=False),
        sa.Column('crawled_at', sa.DateTime(), nullable=False),
        sa.Column('is_processed', sa.Integer(), nullable=False),
        sa.Column('sentiment_score', sa.Integer(), nullable=True),
        sa.Column('relevance_score', sa.Integer(), nullable=True),
        sa.Column('image_url', sa.String(length=1000), nullable=True),
        sa.Column('language', sa.String(length=10), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('url')
    )
    op.create_index('ix_news_articles_title', 'news_articles', ['title'], unique=False)
    op.create_index('ix_news_articles_source', 'news_articles', ['source'], unique=False)
    op.create_index('ix_news_articles_published_at', 'news_articles', ['published_at'], unique=False)

    # Table users
    op.create_table('users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=True),
        sa.Column('email', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Integer(), nullable=False),
        sa.Column('is_admin', sa.Integer(), nullable=False),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('preferences_id', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_username', 'users', ['username'], unique=True)
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # Table user_preferences
    op.create_table('user_preferences',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('theme', sa.String(length=20), nullable=False),
        sa.Column('language', sa.String(length=10), nullable=False),
        sa.Column('timezone', sa.String(length=50), nullable=False),
        sa.Column('default_provider', sa.String(length=50), nullable=False),
        sa.Column('refresh_interval', sa.Integer(), nullable=False),
        sa.Column('max_news_items', sa.Integer(), nullable=False),
        sa.Column('email_notifications', sa.Integer(), nullable=False),
        sa.Column('sound_notifications', sa.Integer(), nullable=False),
        sa.Column('favorite_symbols', sa.String(length=1000), nullable=True),
        sa.Column('dashboard_layout', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_user_preferences_user_id', 'user_preferences', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_user_preferences_user_id', table_name='user_preferences')
    op.drop_table('user_preferences')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_index('ix_users_username', table_name='users')
    op.drop_table('users')
    op.drop_index('ix_news_articles_published_at', table_name='news_articles')
    op.drop_index('ix_news_articles_source', table_name='news_articles')
    op.drop_index('ix_news_articles_title', table_name='news_articles')
    op.drop_table('news_articles')
    op.drop_index('ix_price_alerts_symbol', table_name='price_alerts')
    op.drop_table('price_alerts')
    op.drop_index('ix_alerts_symbol', table_name='alerts')
    op.drop_table('alerts')
    op.drop_index('ix_price_history_market_timestamp', table_name='price_history')
    op.drop_index('ix_price_history_symbol', table_name='price_history')
    op.drop_table('price_history')
    op.drop_index('ix_market_data_symbol', table_name='market_data')
    op.drop_table('market_data')
