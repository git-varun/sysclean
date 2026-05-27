import logging
import os
import pathlib

def get_logger(name: str) -> logging.Logger:
    """Configures and returns a logger for SysClean."""
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers if logger is already configured
    if logger.handlers:
        return logger

    # Determine log level
    env = os.environ.get("SYSCLEAN_ENV", "production").lower()
    raw_level = os.environ.get("SYSCLEAN_LOG_LEVEL", "").upper()

    if env == "development" or env == "dev":
        log_level = logging.DEBUG
    elif raw_level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        log_level = getattr(logging, raw_level)
    else:
        log_level = logging.INFO

    logger.setLevel(log_level)

    # Format
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console Handler
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # File Handler
    log_dir = pathlib.Path.home() / ".local/share/sysclean"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "sysclean.log"
    
    try:
        fh = logging.FileHandler(str(log_file))
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    except Exception as e:
        # Fallback if file logging fails (e.g., permissions)
        logger.warning(f"Could not setup file logging at {log_file}: {e}")

    return logger
