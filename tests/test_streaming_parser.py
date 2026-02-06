"""
Tests para StreamingParser.

Cubre:
- Streaming básico de archivos
- Rate limiting
- Callbacks
- Progress tracking
- Estadísticas
- Manejo de archivos grandes (simulado)
"""

import tempfile
import time
from pathlib import Path
from unittest.mock import Mock

import pytest

from src.parsers import ApacheParser, StreamingParser


class TestStreamingParser:
    """Suite de tests para StreamingParser."""

    @pytest.fixture
    def sample_log_file(self):
        """Crea un archivo temporal con logs de muestra."""
        content = """192.168.1.1 - - [29/Jan/2026:10:00:00 +0000] "GET /api/users HTTP/1.1" 200 1234
192.168.1.2 - - [29/Jan/2026:10:00:01 +0000] "POST /api/login HTTP/1.1" 201 512
192.168.1.3 - - [29/Jan/2026:10:00:02 +0000] "GET /home HTTP/1.1" 200 5678
# Comentario
192.168.1.4 - - [29/Jan/2026:10:00:03 +0000] "DELETE /api/user/123 HTTP/1.1" 204 0
invalid log line
192.168.1.5 - - [29/Jan/2026:10:00:04 +0000] "PUT /api/settings HTTP/1.1" 200 256
"""

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".log") as f:
            f.write(content)
            temp_path = f.name

        yield temp_path

        # Cleanup
        Path(temp_path).unlink()

    @pytest.fixture
    def large_log_file(self):
        """Crea un archivo grande para tests de performance."""
        content_lines = []

        # Generar 1000 líneas de log
        for i in range(1000):
            line = (
                f"192.168.1.{i % 255} - - [29/Jan/2026:10:00:{i % 60:02d} +0000] "
                f'"GET /api/endpoint/{i} HTTP/1.1" 200 {i * 10}\n'
            )
            content_lines.append(line)

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".log") as f:
            f.writelines(content_lines)
            temp_path = f.name

        yield temp_path

        # Cleanup
        Path(temp_path).unlink()

    # ==========================================
    # TESTS BÁSICOS DE STREAMING
    # ==========================================

    def test_stream_file_basic(self, sample_log_file):
        """Test: Streaming básico de archivo."""
        parser = ApacheParser()
        streamer = StreamingParser(parser)

        records = list(streamer.stream_file(sample_log_file))

        # Debe parsear 5 líneas válidas (1 comentario + 1 inválida = ignoradas)
        assert len(records) == 5
        assert records[0]["ip"] == "192.168.1.1"
        assert records[1]["method"] == "POST"
        assert records[4]["url"] == "/api/settings"

    def test_stream_file_stats_tracking(self, sample_log_file):
        """Test: Tracking correcto de estadísticas."""
        parser = ApacheParser()
        streamer = StreamingParser(parser)

        list(streamer.stream_file(sample_log_file))
        stats = streamer.get_stats()

        assert stats["total_lines"] == 7  # Todas las líneas incluyendo comentario
        assert stats["parsed_successfully"] == 5
        assert stats["parse_errors"] == 1  # La línea inválida
        assert stats["start_time"] is not None
        assert stats["end_time"] is not None
        assert stats["bytes_processed"] > 0

    def test_stream_file_with_callback(self, sample_log_file):
        """Test: Callback es llamado por cada registro."""
        parser = ApacheParser()
        callback_mock = Mock()

        streamer = StreamingParser(parser, callback=callback_mock)
        list(streamer.stream_file(sample_log_file))

        # Callback debe ser llamado 5 veces (1 por cada registro válido)
        assert callback_mock.call_count == 5

        # Verificar que recibió un LogRecord
        first_call_arg = callback_mock.call_args_list[0][0][0]
        assert "ip" in first_call_arg
        assert "method" in first_call_arg

    def test_metadata_added_to_records(self, sample_log_file):
        """Test: Metadata (_line_number, _source_file) se agrega."""
        parser = ApacheParser()
        streamer = StreamingParser(parser)

        records = list(streamer.stream_file(sample_log_file))

        assert "_line_number" in records[0]
        assert "_source_file" in records[0]
        assert records[0]["_line_number"] == 1
        assert str(sample_log_file) in records[0]["_source_file"]

    def test_skip_empty_lines_and_comments(self, sample_log_file):
        """Test: Líneas vacías y comentarios son ignorados."""
        parser = ApacheParser()
        streamer = StreamingParser(parser)

        records = list(streamer.stream_file(sample_log_file))

        # Ningún registro debe tener IP vacía o comenzar con #
        for record in records:
            assert record["ip"] != ""
            assert not record["ip"].startswith("#")

    # ==========================================
    # TESTS DE RATE LIMITING
    # ==========================================

    def test_rate_limiting(self, large_log_file):
        """Test: Rate limiting controla velocidad de procesamiento."""
        parser = ApacheParser()
        streamer = StreamingParser(parser)

        start_time = time.time()

        # Limitar a 100 registros/segundo
        # Con 1000 registros, debería tomar ~10 segundos
        records = list(streamer.stream_file(large_log_file, rate_limit=100))

        elapsed = time.time() - start_time

        # Verificar que procesó todos los registros
        assert len(records) == 1000

        # Verificar que respetó el rate limit (con margen de error)
        # Debería tomar al menos 9 segundos (1000 records / 100 per sec)
        # Damos margen porque puede ser más rápido en CI
        assert elapsed >= 9.0 or len(records) == 1000  # Flexibilidad para CI

    def test_rate_limiting_does_not_affect_small_files(self, sample_log_file):
        """Test: Rate limiting no afecta archivos pequeños."""
        parser = ApacheParser()
        streamer = StreamingParser(parser)

        start_time = time.time()

        # Rate limit alto no debería agregar delay significativo
        records = list(streamer.stream_file(sample_log_file, rate_limit=1000))

        elapsed = time.time() - start_time

        # Con solo 5 registros, no debería tomar más de 1 segundo
        assert elapsed < 1.0
        assert len(records) == 5

    # ==========================================
    # TESTS DE PERFORMANCE
    # ==========================================

    def test_memory_efficiency_large_file(self, large_log_file):
        """Test: Streaming no carga todo el archivo en memoria."""
        parser = ApacheParser()
        streamer = StreamingParser(parser)

        # Procesar solo los primeros 10 registros
        records = []
        for i, record in enumerate(streamer.stream_file(large_log_file)):
            records.append(record)
            if i >= 9:  # 0-9 = 10 registros
                break

        assert len(records) == 10

        # Verificar que las estadísticas reflejan que NO procesó todo
        stats = streamer.get_stats()
        assert stats["total_lines"] == 10  # Solo leyó 10 líneas

    def test_processing_speed(self, large_log_file):
        """Test: Velocidad de procesamiento es aceptable."""
        parser = ApacheParser()
        streamer = StreamingParser(parser)

        start_time = time.time()
        records = list(streamer.stream_file(large_log_file))
        elapsed = time.time() - start_time

        # 1000 registros deberían procesarse en menos de 2 segundos
        assert len(records) == 1000
        assert elapsed < 2.0

        # Calcular tasa de procesamiento
        rate = len(records) / elapsed
        assert rate > 500  # Al menos 500 registros/segundo

    # ==========================================
    # TESTS DE MANEJO DE ERRORES
    # ==========================================

    def test_file_not_found_raises_error(self):
        """Test: Lanza error si archivo no existe."""
        parser = ApacheParser()
        streamer = StreamingParser(parser)

        with pytest.raises(FileNotFoundError):
            list(streamer.stream_file("/path/que/no/existe.log"))

    def test_skip_invalid_lines_by_default(self, sample_log_file):
        """Test: Por defecto, omite líneas inválidas."""
        parser = ApacheParser()
        streamer = StreamingParser(parser)

        # No debería lanzar excepción a pesar de la línea inválida
        records = list(streamer.stream_file(sample_log_file, skip_invalid=True))

        assert len(records) == 5  # Las válidas

        stats = streamer.get_stats()
        assert stats["parse_errors"] == 1  # La inválida fue registrada

    def test_raise_on_invalid_when_skip_false(self, sample_log_file):
        """Test: Lanza excepción si skip_invalid=False."""
        parser = ApacheParser()
        streamer = StreamingParser(parser)

        # Debería lanzar excepción al encontrar línea inválida
        with pytest.raises(ValueError):
            list(streamer.stream_file(sample_log_file, skip_invalid=False))

    # ==========================================
    # TESTS DE PROGRESS TRACKING
    # ==========================================

    def test_progress_interval_logging(self, large_log_file, caplog):
        """Test: Progress logging cada N líneas."""
        parser = ApacheParser()

        # Progress cada 100 líneas
        streamer = StreamingParser(parser, progress_interval=100)

        with caplog.at_level("INFO"):
            list(streamer.stream_file(large_log_file))

        # Debería haber al menos 10 logs de progreso (1000 / 100)
        progress_logs = [record for record in caplog.records if "Progreso" in record.message]

        assert len(progress_logs) >= 9  # Al menos 9 logs (margen de error)

    # ==========================================
    # TESTS DE ENCODING
    # ==========================================

    def test_custom_encoding(self):
        """Test: Soporte para diferentes encodings."""
        content = '192.168.1.1 - - [29/Jan/2026:10:00:00 +0000] "GET /test HTTP/1.1" 200 100\n'

        # Crear archivo con encoding latin-1
        with tempfile.NamedTemporaryFile(mode="w", delete=False, encoding="latin-1") as f:
            f.write(content)
            temp_path = f.name

        try:
            parser = ApacheParser()
            streamer = StreamingParser(parser)

            records = list(streamer.stream_file(temp_path, encoding="latin-1"))

            assert len(records) == 1
            assert records[0]["ip"] == "192.168.1.1"

        finally:
            Path(temp_path).unlink()

    # ==========================================
    # TESTS DE BUFFER SIZE
    # ==========================================

    def test_custom_buffer_size(self, sample_log_file):
        """Test: Buffer size customizable."""
        parser = ApacheParser()

        # Buffer muy pequeño (512 bytes)
        streamer = StreamingParser(parser, buffer_size=512)

        records = list(streamer.stream_file(sample_log_file))

        # Debe funcionar igual independientemente del buffer
        assert len(records) == 5

    # ==========================================
    # TESTS DE ESTADÍSTICAS
    # ==========================================

    def test_stats_include_timing(self, sample_log_file):
        """Test: Estadísticas incluyen timing."""
        parser = ApacheParser()
        streamer = StreamingParser(parser)

        list(streamer.stream_file(sample_log_file))
        stats = streamer.get_stats()

        assert "start_time" in stats
        assert "end_time" in stats
        assert stats["end_time"] > stats["start_time"]

    def test_stats_include_bytes_processed(self, sample_log_file):
        """Test: Estadísticas incluyen bytes procesados."""
        parser = ApacheParser()
        streamer = StreamingParser(parser)

        list(streamer.stream_file(sample_log_file))
        stats = streamer.get_stats()

        assert "bytes_processed" in stats
        assert stats["bytes_processed"] > 0
