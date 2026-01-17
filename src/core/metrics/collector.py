"""
Advanced metrics collector with PostgreSQL storage.
Main class that handles metric collection and persistence.
"""

import time
import threading
import json
import random
import inspect
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
from io import StringIO
import csv
import contextlib

import psycopg2
from psycopg2.extras import RealDictCursor, Json
from psycopg2.pool import SimpleConnectionPool

from .types import (
    Metric, MetricAggregate, MetricType, MetricLevel,
    MetricValue, TagsDict
)
from src.core.exceptions import MetricsError
from src.core.logger import get_logger

logger = get_logger(__name__)


class AdvancedMetricsCollector:
    """
    Advanced metrics collector with:
    - Buffered storage
    - Automatic flushing
    - Thread safety
    - Connection pooling
    - In-memory aggregation
    """

    def __init__(
        self,
        db_config: Dict[str, Any],
        batch_size: int = 1000,
        flush_interval: int = 60,
        max_buffer_size: int = 10000,
        retention_days: int = 30,
        enable_aggregation: bool = True,
        max_workers: int = 2,
        max_connections: int = 5
    ):
        """
        Initialize the advanced metrics collector.

        Args:
            db_config: PostgreSQL connection configuration
            batch_size: Number of metrics per batch insert
            flush_interval: Auto-flush interval in seconds
            max_buffer_size: Maximum buffer size before forced flush
            retention_days: Days to keep metrics before auto-deletion
            enable_aggregation: Enable in-memory aggregation
            max_workers: Thread pool workers for background tasks
            max_connections: Maximum database connections in pool
        """
        self.db_config = db_config
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.max_buffer_size = max_buffer_size
        self.retention_days = retention_days
        self.enable_aggregation = enable_aggregation

        # Thread-safe buffer
        self.metrics_buffer: List[Metric] = []
        self.buffer_lock = threading.RLock()
        self.last_flush = datetime.now()
        self.flush_condition = threading.Condition(self.buffer_lock)

        # Statistics
        self.stats = {
            'total_metrics': 0,
            'total_inserted': 0,
            'total_errors': 0,
            'buffer_overflow': 0,
            'last_flush_time': None,
            'aggregates_count': 0,
            'flush_count': 0,
            'background_flushes': 0
        }

        # In-memory aggregation
        self.aggregates: Dict[str, MetricAggregate] = {}
        self.aggregate_lock = threading.RLock()

        # Background processing
        self.executor = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="metrics-worker"
        )
        self.flush_thread = None
        self.running = False

        # Connection pool
        self.connection_pool = None
        self.max_connections = max_connections
        self._init_connection_pool()

        # Initialize metrics table
        self._init_metrics_table()

        logger.info(
            "MetricsCollector inicializado",
            batch_size=batch_size,
            flush_interval=flush_interval,
            max_buffer_size=max_buffer_size,
            max_connections=max_connections
        )

    def _init_connection_pool(self) -> None:
        """Initialize PostgreSQL connection pool."""
        try:
            self.connection_pool = SimpleConnectionPool(
                minconn=1,
                maxconn=self.max_connections,
                **self.db_config
            )
            logger.debug("Connection pool inicializado")
        except Exception as e:
            logger.error("Error inicializando connection pool", error=str(e))
            raise MetricsError(f"Failed to initialize connection pool: {e}")

    @contextlib.contextmanager
    def _get_connection(self):
        """Get a connection from the pool with context manager."""
        conn = None
        try:
            conn = self.connection_pool.getconn()
            yield conn
        except Exception as e:
            logger.error("Error obteniendo conexión del pool", error=str(e))
            raise
        finally:
            if conn:
                self.connection_pool.putconn(conn)

    def _init_metrics_table(self) -> None:
        """Initialize metrics table schema if not exists."""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    # Create main metrics table
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS metrics (
                            id BIGSERIAL PRIMARY KEY,
                            name VARCHAR(255) NOT NULL,
                            value DOUBLE PRECISION NOT NULL,
                            metric_type VARCHAR(50) NOT NULL,
                            timestamp TIMESTAMPTZ NOT NULL,
                            tags JSONB DEFAULT '{}'::jsonb,
                            level VARCHAR(50) DEFAULT 'info',
                            description TEXT,
                            source VARCHAR(255),
                            unit VARCHAR(50),
                            metadata JSONB DEFAULT '{}'::jsonb,
                            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                            INDEX idx_metrics_timestamp (timestamp),
                            INDEX idx_metrics_name (name),
                            INDEX idx_metrics_type (metric_type),
                            INDEX idx_metrics_level (level),
                            INDEX idx_metrics_tags USING GIN (tags),
                            INDEX idx_metrics_metadata USING GIN (metadata)
                        );
                    """)

                    # Create daily aggregates table
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS metrics_daily_aggregates (
                            date DATE NOT NULL,
                            name VARCHAR(255) NOT NULL,
                            metric_type VARCHAR(50) NOT NULL,
                            count BIGINT NOT NULL,
                            sum DOUBLE PRECISION NOT NULL,
                            avg DOUBLE PRECISION NOT NULL,
                            min DOUBLE PRECISION NOT NULL,
                            max DOUBLE PRECISION NOT NULL,
                            p95 DOUBLE PRECISION,
                            p99 DOUBLE PRECISION,
                            tags JSONB,
                            PRIMARY KEY (date, name, metric_type),
                            INDEX idx_daily_agg_date (date),
                            INDEX idx_daily_agg_name (name)
                        );
                    """)

                    # Create retention policy
                    cursor.execute(f"""
                        CREATE OR REPLACE FUNCTION cleanup_old_metrics()
                        RETURNS void AS $$
                        BEGIN
                            DELETE FROM metrics
                            WHERE timestamp < NOW() - INTERVAL '{self.retention_days} days';

                            DELETE FROM metrics_daily_aggregates
                            WHERE date < NOW() - INTERVAL '{self.retention_days} days';
                        END;
                        $$ LANGUAGE plpgsql;
                    """)

                    conn.commit()
                    logger.info("Esquema de métricas inicializado")

        except Exception as e:
            logger.error("Error inicializando esquema de métricas", error=str(e))
            raise MetricsError(f"Failed to initialize metrics schema: {e}")

    def start_background_flush(self) -> None:
        """Start background flush thread."""
        if self.flush_thread and self.flush_thread.is_alive():
            return

        self.running = True
        self.flush_thread = threading.Thread(
            target=self._background_flush_loop,
            daemon=True,
            name="metrics-flush-daemon"
        )
        self.flush_thread.start()
        logger.info("Background flush thread iniciado")

    def stop_background_flush(self) -> None:
        """Stop background flush thread."""
        self.running = False
        if self.flush_thread:
            with self.flush_condition:
                self.flush_condition.notify_all()
            self.flush_thread.join(timeout=10)
            logger.info("Background flush thread detenido")

    def _background_flush_loop(self) -> None:
        """Background flush loop for automatic flushing."""
        logger.debug("Background flush loop iniciado")

        while self.running:
            try:
                # Wait for flush interval or buffer size trigger
                with self.flush_condition:
                    buffer_size = len(self.metrics_buffer)
                    time_since_flush = (datetime.now() - self.last_flush).total_seconds()

                    should_flush = (
                        buffer_size >= self.batch_size or
                        time_since_flush >= self.flush_interval
                    )

                    if not should_flush:
                        # Wait for timeout or notification
                        wait_time = min(
                            self.flush_interval - time_since_flush,
                            self.flush_interval
                        )
                        if wait_time > 0:
                            self.flush_condition.wait(timeout=wait_time)

                # Check again if we should flush
                with self.buffer_lock:
                    buffer_size = len(self.metrics_buffer)
                    time_since_flush = (datetime.now() - self.last_flush).total_seconds()

                    should_flush = (
                        buffer_size >= self.batch_size or
                        time_since_flush >= self.flush_interval or
                        buffer_size > 0 and not self.running
                    )

                if should_flush:
                    self.stats['background_flushes'] += 1
                    self.flush()

                # Small sleep to prevent CPU spinning
                time.sleep(0.1)

            except Exception as e:
                logger.error("Error en background flush loop", error=str(e))
                time.sleep(5)  # Backoff on error

    def record_metric(
        self,
        name: str,
        value: MetricValue,
        metric_type: MetricType = MetricType.GAUGE,
        tags: Optional[TagsDict] = None,
        level: MetricLevel = MetricLevel.INFO,
        description: Optional[str] = None,
        source: Optional[str] = None,
        unit: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ) -> None:
        """
        Record a metric with all metadata.

        Args:
            name: Metric name (e.g., "etl.records.processed")
            value: Numeric value
            metric_type: Type of metric
            tags: Dimension tags for segmentation
            level: Importance level
            description: Human-readable description
            source: Source component
            unit: Unit of measurement
            metadata: Additional metadata
            timestamp: Optional custom timestamp
        """
        try:
            # Validate input
            if not isinstance(value, (int, float)):
                raise MetricsError(f"Metric value must be numeric: {value}")

            if not name or not name.strip():
                raise MetricsError("Metric name cannot be empty")

            # Create metric object
            metric = Metric(
                name=name.strip(),
                value=float(value),
                metric_type=metric_type,
                timestamp=timestamp or datetime.now(),
                tags=tags or {},
                level=level,
                description=description,
                source=source or self._get_caller_source(),
                unit=unit,
                metadata=metadata or {}
            )

            # Add to buffer
            with self.buffer_lock:
                # Check buffer limits
                if len(self.metrics_buffer) >= self.max_buffer_size:
                    self.stats['buffer_overflow'] += 1
                    logger.warning(
                        "Buffer de métricas lleno, forzando flush",
                        buffer_size=len(self.metrics_buffer),
                        max_buffer_size=self.max_buffer_size
                    )
                    self.flush(force=True)

                self.metrics_buffer.append(metric)
                self.stats['total_metrics'] += 1

                # Update in-memory aggregates
                if self.enable_aggregation:
                    self._update_aggregate(metric)

                # Notify background thread if buffer is getting full
                if len(self.metrics_buffer) >= self.batch_size:
                    with self.flush_condition:
                        self.flush_condition.notify()

            # Log high-level metrics
            if level in (MetricLevel.ERROR, MetricLevel.CRITICAL):
                logger.warning(
                    "Métrica de error registrada",
                    name=name,
                    value=value,
                    level=level.value
                )

        except Exception as e:
            logger.error(
                "Error registrando métrica",
                name=name,
                value=value,
                error=str(e),
                exc_info=True
            )
            self.stats['total_errors'] += 1
            raise MetricsError(f"Failed to record metric '{name}': {e}")

    def _get_caller_source(self) -> str:
        """Get the calling module/function as source."""
        try:
            # Walk up the stack to find the first non-metrics caller
            for frame_info in inspect.stack():
                frame = frame_info.frame
                module = inspect.getmodule(frame)
                if module and 'metrics' not in module.__name__:
                    # Return formatted source: module.function
                    func_name = frame_info.function
                    if func_name == '<module>':
                        return module.__name__.split('.')[-1]
                    return f"{module.__name__.split('.')[-1]}.{func_name}"
        except Exception:
            pass
        return "unknown"

    def _update_aggregate(self, metric: Metric) -> None:
        """Update in-memory aggregates."""
        aggregate_key = f"{metric.name}:{metric.metric_type.value}"

        with self.aggregate_lock:
            if aggregate_key not in self.aggregates:
                self.aggregates[aggregate_key] = MetricAggregate(
                    name=metric.name,
                    metric_type=metric.metric_type
                )
                self.stats['aggregates_count'] = len(self.aggregates)

            self.aggregates[aggregate_key].update(metric)

    def flush(self, force: bool = False) -> int:
        """
        Flush buffered metrics to PostgreSQL.

        Args:
            force: Force flush even if buffer is small

        Returns:
            Number of metrics inserted
        """
        # Get metrics from buffer
        with self.buffer_lock:
            if not self.metrics_buffer and not force:
                return 0

            metrics_to_flush = self.metrics_buffer.copy()
            self.metrics_buffer.clear()

            if not metrics_to_flush:
                return 0

        logger.debug(
            "Iniciando flush de métricas",
            count=len(metrics_to_flush),
            force=force
        )

        try:
            inserted_count = self._bulk_insert_metrics(metrics_to_flush)

            # Update statistics
            with self.buffer_lock:
                self.stats['total_inserted'] += inserted_count
                self.stats['flush_count'] += 1
                self.last_flush = datetime.now()
                self.stats['last_flush_time'] = self.last_flush

            logger.info(
                "Flush completado exitosamente",
                inserted=inserted_count,
                total_inserted=self.stats['total_inserted']
            )

            return inserted_count

        except Exception as e:
            logger.error(
                "Error en flush de métricas",
                error=str(e),
                count=len(metrics_to_flush),
                exc_info=True
            )

            # Return metrics to buffer for retry
            with self.buffer_lock:
                self.metrics_buffer.extend(metrics_to_flush)

            self.stats['total_errors'] += 1
            raise MetricsError(f"Failed to flush metrics: {e}")

    def _bulk_insert_metrics(self, metrics: List[Metric]) -> int:
        """Bulk insert metrics using COPY for maximum performance."""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    # Prepare data for COPY
                    csv_buffer = StringIO()
                    writer = csv.writer(csv_buffer, delimiter='\t')

                    for metric in metrics:
                        writer.writerow([
                            metric.name,
                            metric.value,
                            metric.metric_type.value,
                            metric.timestamp,
                            json.dumps(metric.tags),
                            metric.level.value,
                            metric.description or '',
                            metric.source or '',
                            metric.unit or '',
                            json.dumps(metric.metadata)
                        ])

                    csv_buffer.seek(0)

                    # Execute COPY command
                    cursor.copy_from(
                        csv_buffer,
                        'metrics',
                        columns=[
                            'name', 'value', 'metric_type', 'timestamp',
                            'tags', 'level', 'description', 'source',
                            'unit', 'metadata'
                        ]
                    )

                    conn.commit()
                    return len(metrics)

        except psycopg2.Error as e:
            logger.error(
                "Error de PostgreSQL en bulk insert",
                error=str(e),
                pgcode=e.pgcode if hasattr(e, 'pgcode') else None
            )
            raise

    def get_metrics_summary(
        self,
        hours: int = 24,
        name_filter: Optional[str] = None,
        metric_type: Optional[MetricType] = None,
        level: Optional[MetricLevel] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Get detailed metrics summary with filtering.

        Args:
            hours: Hours to look back
            name_filter: Filter by metric name (LIKE pattern)
            metric_type: Filter by metric type
            level: Filter by level
            limit: Maximum results

        Returns:
            Dictionary with metrics summary
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    # Build query with filters
                    query = """
                    SELECT
                        name,
                        metric_type,
                        COUNT(*) as count,
                        AVG(value) as avg_value,
                        MIN(value) as min_value,
                        MAX(value) as max_value,
                        PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY value) as p95,
                        PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY value) as p99,
                        SUM(CASE WHEN level = 'error' THEN 1 ELSE 0 END) as error_count,
                        SUM(CASE WHEN level = 'warning' THEN 1 ELSE 0 END) as warning_count,
                        MIN(timestamp) as first_seen,
                        MAX(timestamp) as last_seen,
                        (SELECT tags FROM metrics m2
                         WHERE m2.name = metrics.name
                         ORDER BY timestamp DESC LIMIT 1) as latest_tags
                    FROM metrics
                    WHERE timestamp > NOW() - INTERVAL %s
                    """

                    params: List[Any] = [f"{hours} hours"]

                    # Apply filters
                    if name_filter:
                        query += " AND name LIKE %s"
                        params.append(f"%{name_filter}%")

                    if metric_type:
                        query += " AND metric_type = %s"
                        params.append(metric_type.value)

                    if level:
                        query += " AND level = %s"
                        params.append(level.value)

                    # Group and limit
                    query += """
                    GROUP BY name, metric_type
                    ORDER BY count DESC
                    LIMIT %s;
                    """
                    params.append(limit)

                    cursor.execute(query, params)
                    results = cursor.fetchall()

                    # Build summary
                    summary = {
                        'period_hours': hours,
                        'total_metrics': sum(r['count'] for r in results),
                        'unique_metrics': len(results),
                        'error_metrics': sum(r['error_count'] for r in results),
                        'warning_metrics': sum(r['warning_count'] for r in results),
                        'timestamp': datetime.now().isoformat(),
                        'metrics': []
                    }

                    for row in results:
                        metric_summary = {
                            'name': row['name'],
                            'type': row['metric_type'],
                            'count': row['count'],
                            'avg': float(row['avg_value']) if row['avg_value'] else 0,
                            'min': float(row['min_value']) if row['min_value'] else 0,
                            'max': float(row['max_value']) if row['max_value'] else 0,
                            'p95': float(row['p95']) if row['p95'] else None,
                            'p99': float(row['p99']) if row['p99'] else None,
                            'error_count': row['error_count'],
                            'warning_count': row['warning_count'],
                            'first_seen': row['first_seen'].isoformat() if row['first_seen'] else None,
                            'last_seen': row['last_seen'].isoformat() if row['last_seen'] else None,
                            'latest_tags': row['latest_tags']
                        }
                        summary['metrics'].append(metric_summary)

                    return summary

        except Exception as e:
            logger.error("Error obteniendo resumen de métricas", error=str(e))
            raise MetricsError(f"Failed to get metrics summary: {e}")

    def get_aggregates(self) -> Dict[str, Any]:
        """Get in-memory aggregates."""
        with self.aggregate_lock:
            return {
                key: {
                    'name': agg.name,
                    'type': agg.metric_type.value,
                    'count': agg.count,
                    'sum': agg.sum,
                    'avg': agg.avg,
                    'min': agg.min,
                    'max': agg.max,
                    'last_value': agg.last_value,
                    'first_seen': agg.first_seen.isoformat() if agg.first_seen else None,
                    'last_seen': agg.last_seen.isoformat() if agg.last_seen else None
                }
                for key, agg in self.aggregates.items()
            }

    def get_stats(self) -> Dict[str, Any]:
        """Get collector statistics."""
        with self.buffer_lock:
            buffer_size = len(self.metrics_buffer)
            with self.aggregate_lock:
                aggregates_count = len(self.aggregates)

            return {
                'collector': {
                    'buffer_size': buffer_size,
                    'total_metrics': self.stats['total_metrics'],
                    'total_inserted': self.stats['total_inserted'],
                    'total_errors': self.stats['total_errors'],
                    'buffer_overflow': self.stats['buffer_overflow'],
                    'flush_count': self.stats['flush_count'],
                    'background_flushes': self.stats['background_flushes'],
                    'last_flush_time': self.stats['last_flush_time'],
                    'aggregates_count': aggregates_count,
                    'running': self.running,
                    'flush_interval': self.flush_interval,
                    'batch_size': self.batch_size
                },
                'aggregates': self.get_aggregates()
            }

    def health_check(self) -> Dict[str, Any]:
        """Perform health check of the collector."""
        try:
            # Test database connection
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    db_ok = cursor.fetchone()[0] == 1

            with self.buffer_lock:
                buffer_health = len(self.metrics_buffer) < self.max_buffer_size * 0.8

            return {
                'status': 'healthy',
                'database': 'connected' if db_ok else 'disconnected',
                'buffer_health': 'ok' if buffer_health else 'warning',
                'buffer_size': len(self.metrics_buffer),
                'background_thread': 'running' if self.running else 'stopped',
                'last_flush': self.stats['last_flush_time'],
                'total_inserted': self.stats['total_inserted'],
                'total_errors': self.stats['total_errors']
            }

        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'database': 'disconnected',
                'buffer_size': len(self.metrics_buffer)
            }

    def cleanup_old_metrics(self) -> int:
        """Clean up old metrics based on retention policy."""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT cleanup_old_metrics()")
                    conn.commit()
                    logger.info("Limpieza de métricas antiguas ejecutada")
                    return 1
        except Exception as e:
            logger.error("Error limpiando métricas antiguas", error=str(e))
            return 0

    def __enter__(self):
        """Context manager entry."""
        self.start_background_flush()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        # Force final flush
        try:
            self.flush(force=True)
        except Exception as e:
            logger.error("Error en flush final", error=str(e))

        # Stop background thread
        self.stop_background_flush()

        # Cleanup
        if self.executor:
            self.executor.shutdown(wait=True)

        logger.info("MetricsCollector cerrado")

    def close(self):
        """Explicit close method."""
        self.__exit__(None, None, None)
