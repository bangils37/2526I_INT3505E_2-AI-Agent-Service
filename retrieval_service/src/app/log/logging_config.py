# retrieval_service/src/app/log/logging_config.py
# -*- coding: utf-8 -*-
"""
Cấu hình logging cho toàn bộ ứng dụng.
"""
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


class ColorFormatter(logging.Formatter):
    """Formatter thêm màu cho log ra terminal.

    Attributes:
        COLORS (dict): Mapping level log -> ANSI escape code màu.
        RESET (str): Ký tự reset màu ANSI.
    """
    COLORS = {
        logging.DEBUG: "\033[37m",     # xám
        logging.INFO: "\033[36m",      # cyan
        logging.WARNING: "\033[33m",   # vàng
        logging.ERROR: "\033[31m",     # đỏ
        logging.CRITICAL: "\033[41m",  # nền đỏ
    }
    RESET = "\033[0m"

    def format(self, record):
        """Thêm màu sắc vào message log.

        Args:
            record (logging.LogRecord): Bản ghi log.

        Returns:
            str: Chuỗi log đã được thêm màu.
        """
        color = self.COLORS.get(record.levelno, self.RESET)
        message = super().format(record)
        return f"{color}{message}{self.RESET}"


def setup_logging(
    log_level: int = logging.INFO,
    log_file: str = "app.log",
    max_bytes: int = 5 * 1024 * 1024,
    backup_count: int = 5
) -> None:
    """Cấu hình logging cho toàn bộ ứng dụng.

    Bao gồm:
    - Ghi log ra file với xoay vòng (rotating file handler).
    - In log ra console với màu sắc.
    - Gắn loggers của uvicorn.

    Args:
        log_level (int, optional): Mức log mặc định. Defaults to logging.INFO.
        log_file (str, optional): Tên file log. Defaults to "app.log".
        max_bytes (int, optional): Dung lượng tối đa mỗi file log (bytes). Defaults to 5MB.
        backup_count (int, optional): Số lượng file log xoay vòng giữ lại. Defaults to 5.
    """
    # ------------------------------
    # Tạo thư mục logs
    # ------------------------------
    log_dir = Path(__file__).resolve().parents[3] / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / log_file

    # ------------------------------
    # File handler (không màu)
    # ------------------------------
    file_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
    )
    file_handler = RotatingFileHandler(
        log_path, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
    )
    file_handler.setFormatter(file_formatter)

    # ------------------------------
    # Console handler (có màu)
    # ------------------------------
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        ColorFormatter("%(asctime)s [%(levelname)s] %(name)s - %(message)s")
    )

    # ------------------------------
    # Root logger
    # ------------------------------
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers = [console_handler, file_handler]

    # ------------------------------
    # Gắn thêm cho uvicorn loggers
    # ------------------------------
    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        uvicorn_logger = logging.getLogger(logger_name)
        uvicorn_logger.setLevel(log_level)
        uvicorn_logger.handlers = [console_handler, file_handler]
        # 🧩 Giữ propagate=True cho uvicorn.access để thấy HTTP logs
        if logger_name == "uvicorn.access":
            uvicorn_logger.propagate = True
        else:
            uvicorn_logger.propagate = False

    logging.getLogger(__name__).info("Logging initialized, file: %s", log_path)
