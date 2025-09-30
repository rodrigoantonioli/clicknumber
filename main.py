import logging
import os
import random
import signal
import sys
import time
from typing import Optional

import requests


DEFAULT_TARGET_URL = "https://camo.githubusercontent.com/6279ae4e6a1047e5bf8fca8f257562d182f64c83def68a33c2d26b295fd54fad/68747470733a2f2f6b6f6d617265762e636f6d2f67687076632f3f757365726e616d653d726f647269676f616e746f6e696f6c69267374796c653d666c6174"


def _env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        parsed = float(value)
    except ValueError as exc:
        raise ValueError(f"Env var {name} must be a float, got: {value!r}") from exc
    if parsed <= 0:
        raise ValueError(f"Env var {name} must be > 0, got: {parsed}")
    return parsed


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        parsed = int(value)
    except ValueError as exc:
        raise ValueError(f"Env var {name} must be an integer, got: {value!r}") from exc
    if parsed <= 0:
        raise ValueError(f"Env var {name} must be > 0, got: {parsed}")
    return parsed


class Pinger:
    def __init__(self, url: str, min_interval: float, max_interval: float, timeout: float, method: str = "GET") -> None:
        if not url:
            raise ValueError("URL must not be empty")
        if min_interval > max_interval:
            raise ValueError("min_interval must be <= max_interval")
        self.url = url
        self.min_interval = min_interval
        self.max_interval = max_interval
        self.timeout = timeout
        self.method = method.upper()
        self._stop = False
        self.session = requests.Session()

    def stop(self, *_: object) -> None:
        logging.info("Stop signal received, shutting down...")
        self._stop = True

    def run(self) -> None:
        logging.info(
            "Starting pinger: url=%s, method=%s, min_interval=%.2fs, max_interval=%.2fs, timeout=%.2fs",
            self.url,
            self.method,
            self.min_interval,
            self.max_interval,
            self.timeout,
        )
        while not self._stop:
            started_at = time.perf_counter()
            try:
                response = self.session.request(self.method, self.url, timeout=self.timeout)
                elapsed = time.perf_counter() - started_at
                logging.info("%s %s -> %s in %.3fs", self.method, self.url, response.status_code, elapsed)
            except requests.RequestException as exc:
                elapsed = time.perf_counter() - started_at
                logging.warning("%s %s failed after %.3fs: %s", self.method, self.url, elapsed, exc)

            sleep_for = random.uniform(self.min_interval, self.max_interval)
            logging.debug("Sleeping for %.3fs", sleep_for)
            self._sleep_until_stop(sleep_for)

    def _sleep_until_stop(self, seconds: float) -> None:
        end_time = time.perf_counter() + seconds
        while not self._stop and time.perf_counter() < end_time:
            time.sleep(min(0.2, end_time - time.perf_counter()))


def configure_logging(level: Optional[str] = None) -> None:
    log_level = level or os.getenv("LOG_LEVEL", "INFO")
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )


def main() -> None:
    configure_logging()

    url = os.getenv("TARGET_URL")
    if not url:
        logging.info("TARGET_URL not set, falling back to default target")
        url = DEFAULT_TARGET_URL

    min_interval = _env_float("MIN_INTERVAL", 1.0)
    max_interval = _env_float("MAX_INTERVAL", 3.0)
    timeout = _env_float("REQUEST_TIMEOUT", 5.0)
    method = os.getenv("HTTP_METHOD", "GET")

    if min_interval > max_interval:
        logging.error("MIN_INTERVAL (%.2f) must be <= MAX_INTERVAL (%.2f)", min_interval, max_interval)
        sys.exit(1)

    pinger = Pinger(url=url, min_interval=min_interval, max_interval=max_interval, timeout=timeout, method=method)

    signal.signal(signal.SIGINT, pinger.stop)
    signal.signal(signal.SIGTERM, pinger.stop)

    try:
        pinger.run()
    except KeyboardInterrupt:
        pinger.stop()


if __name__ == "__main__":
    main()
