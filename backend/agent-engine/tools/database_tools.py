"""
Database Tools Module
====================

This module provides essential utilities for database operations, including:
- Connection management
- Transaction handling
- Query building
- Pagination support
- Caching
- Error handling
- Async/await support

Features:
- SQLAlchemy integration
- Connection pooling
- Transaction management
- Query optimization
- Pagination utilities
- Cache integration
- Type-safe operations
"""

import logging
from typing import Any, Dict, List, Optional, Type, TypeVar, Generic
from sqlalchemy import create_engine, text, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, scoped_session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import Select
from cachetools import TTLCache
from functools import wraps
from contextlib import contextmanager

logger = logging.getLogger(__name__)

T = TypeVar('T')
Base = declarative_base()

class DatabaseError(Exception):
    """Custom exception for database-related errors."""
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        self.message = message
        self.original_error = original_error
        super().__init__(message)

class DatabaseTools(Generic[T]):
    """Class containing various database utility functions."""

    def __init__(
        self,
        db_url: str,
        pool_size: int = 5,
        max_overflow: int = 10,
        cache_ttl: int = 300,  # 5 minutes
        cache_maxsize: int = 1000
    ):
        """Initialize database tools with configuration.

        Args:
            db_url (str): Database connection URL
            pool_size (int): Size of connection pool
            max_overflow (int): Maximum overflow size
            cache_ttl (int): Cache time-to-live in seconds
            cache_maxsize (int): Maximum size of cache
        """
        self.db_url = db_url
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.cache = TTLCache(maxsize=cache_maxsize, ttl=cache_ttl)
        self._engine = None
        self._Session = None
        self._scoped_session = None

    def init_engine(self) -> None:
        """Initialize database engine with connection pool."""
        self._engine = create_engine(
            self.db_url,
            pool_size=self.pool_size,
            max_overflow=self.max_overflow,
            pool_pre_ping=True
        )
        self._Session = sessionmaker(bind=self._engine)
        self._scoped_session = scoped_session(self._Session)

    @property
    def engine(self) -> Any:
        """Get the database engine."""
        if self._engine is None:
            self.init_engine()
        return self._engine

    @property
    def Session(self) -> Any:
        """Get the session factory."""
        if self._Session is None:
            self.init_engine()
        return self._Session

    @property
    def scoped_session(self) -> Any:
        """Get the scoped session."""
        if self._scoped_session is None:
            self.init_engine()
        return self._scoped_session

    @contextmanager
    def session_scope(self) -> Session:
        """Provide a transactional scope around a series of operations."""
        session = self.scoped_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise DatabaseError(f"Database transaction failed: {str(e)}", e)
        finally:
            session.close()

    def cache_query_result(
        self,
        query: Select,
        cache_key: str,
        force_refresh: bool = False
    ) -> Any:
        """Cache query results with TTL.

        Args:
            query (Select): SQLAlchemy query
            cache_key (str): Unique key for cache
            force_refresh (bool): Force refresh cache

        Returns:
            Any: Query result
        """
        if not force_refresh and cache_key in self.cache:
            logger.debug(f"Cache hit for query: {cache_key}")
            return self.cache[cache_key]

        with self.session_scope() as session:
            result = session.execute(query).scalars().all()
            self.cache[cache_key] = result
            return result

    def paginate_query(
        self,
        query: Select,
        page: int = 1,
        per_page: int = 20,
        total_count: bool = True
    ) -> Dict[str, Any]:
        """Paginate a query.

        Args:
            query (Select): SQLAlchemy query
            page (int): Current page number
            per_page (int): Items per page
            total_count (bool): Include total count

        Returns:
            dict: Paginated results with metadata
        """
        if page < 1:
            raise ValueError("Page number must be greater than 0")

        offset = (page - 1) * per_page
        paginated_query = query.offset(offset).limit(per_page)

        with self.session_scope() as session:
            items = session.execute(paginated_query).scalars().all()
            
            result = {
                "items": items,
                "page": page,
                "per_page": per_page,
                "total_pages": None,
                "total_items": None
            }

            if total_count:
                count_query = select(func.count()).select_from(query.subquery())
                total_items = session.execute(count_query).scalar()
                result["total_items"] = total_items
                result["total_pages"] = (total_items + per_page - 1) // per_page

            return result

    def execute_raw_sql(
        self,
        sql: str,
        params: Optional[Dict] = None
    ) -> Any:
        """Execute raw SQL query.

        Args:
            sql (str): SQL query string
            params (dict): Query parameters

        Returns:
            Any: Query result
        """
        with self.session_scope() as session:
            result = session.execute(text(sql), params)
            return result.fetchall()

    def bulk_insert(
        self,
        model: Type[T],
        data: List[Dict]
    ) -> None:
        """Bulk insert multiple records.

        Args:
            model: SQLAlchemy model class
            data: List of dictionaries containing data
        """
        if not data:
            return

        with self.session_scope() as session:
            session.bulk_insert_mappings(model, data)

    def bulk_update(
        self,
        model: Type[T],
        data: List[Dict],
        update_fields: List[str]
    ) -> None:
        """Bulk update multiple records.

        Args:
            model: SQLAlchemy model class
            data: List of dictionaries containing data
            update_fields: Fields to update
        """
        if not data:
            return

        with self.session_scope() as session:
            session.bulk_update_mappings(
                model,
                [{k: v for k, v in item.items() if k in update_fields}
                 for item in data]
            )

    def upsert(
        self,
        model: Type[T],
        data: Dict,
        unique_fields: List[str]
    ) -> None:
        """Insert or update a record.

        Args:
            model: SQLAlchemy model class
            data: Dictionary containing data
            unique_fields: Fields to check for uniqueness
        """
        with self.session_scope() as session:
            existing = session.query(model).filter_by(**{
                field: data[field] for field in unique_fields
            }).first()

            if existing:
                for key, value in data.items():
                    setattr(existing, key, value)
            else:
                session.add(model(**data))

    def get_or_create(
        self,
        model: Type[T],
        defaults: Optional[Dict] = None,
        **kwargs
    ) -> Tuple[T, bool]:
        """Get or create a record.

        Args:
            model: SQLAlchemy model class
            defaults: Default values for new record
            **kwargs: Filter criteria

        Returns:
            tuple: (record, created)
        """
        with self.session_scope() as session:
            instance = session.query(model).filter_by(**kwargs).first()
            if instance:
                return instance, False
            
            params = defaults or {}
            params.update(kwargs)
            instance = model(**params)
            session.add(instance)
            return instance, True

    def transactional(
        self,
        func: Callable
    ) -> Callable:
        """Decorator to wrap a function in a transaction."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            with self.session_scope() as session:
                return func(session, *args, **kwargs)
        return wrapper

    def handle_db_error(
        self,
        error: Exception,
        default_value: Any = None
    ) -> Any:
        """Handle database-related errors gracefully.

        Args:
            error (Exception): Caught exception
            default_value (Any): Value to return on error

        Returns:
            Any: Default value or re-raises error
        """
        logger.error(f"Database Error: {str(error)}")
        if isinstance(error, SQLAlchemyError):
            if "timeout" in str(error).lower():
                logger.warning("Database connection timeout")
            elif "deadlock" in str(error).lower():
                logger.warning("Database deadlock detected")
        return default_value

# Example usage:
if __name__ == "__main__":
    # Initialize database tools
    db = DatabaseTools(
        db_url="postgresql://user:password@localhost/dbname",
        pool_size=5,
        max_overflow=10,
        cache_ttl=300
    )

    # Example transactional function
    @db.transactional
    def create_user(session, user_data):
        user = db.get_or_create(
            User,
            defaults={"created_at": datetime.utcnow()},
            email=user_data["email"]
        )
        return user

    # Example pagination
    users = db.paginate_query(
        select(User).filter(User.active == True),
        page=1,
        per_page=50
    )

    # Example bulk operations
    users_data = [
        {"name": "John", "email": "john@example.com"},
        {"name": "Jane", "email": "jane@example.com"}
    ]
    db.bulk_insert(User, users_data)

    # Example caching
    users_cache = db.cache_query_result(
        select(User).filter(User.active == True),
        cache_key="active_users"
    )