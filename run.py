import logging
import socket
import threading
from typing import Optional

import numpy as np
from flask_socketio import SocketIO

from app import create_app

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
)
logger = logging.getLogger("tc_generator")

app = create_app()
socketio = SocketIO(app, cors_allowed_origins="*")


class SignalDetector:
    """Detect a valid RF signal in the FFT magnitude spectrum.

    The detector uses hysteresis and a minimum active-bin ratio to reduce false
    positives caused by noise and spurious packet content.
    """

    def __init__(
        self,
        detect_threshold_db: float = -35.0,
        release_threshold_db: float = -50.0,
        active_bins_ratio: float = 0.02,
        noise_margin_db: float = 8.0,
    ) -> None:
        self.detect_threshold_db = detect_threshold_db
        self.release_threshold_db = release_threshold_db
        self.active_bins_ratio = active_bins_ratio
        self.noise_margin_db = noise_margin_db

    def detect(self, magnitude_db: np.ndarray) -> Optional[bool]:
        """Return True, False, or None based on the current signal state."""
        if magnitude_db.size == 0:
            return None

        noise_floor_db = float(np.median(magnitude_db))
        active_bins = magnitude_db > (noise_floor_db + self.noise_margin_db)
        active_ratio = float(np.mean(active_bins)) if active_bins.size else 0.0
        peak_db = float(np.max(magnitude_db))

        if peak_db >= self.detect_threshold_db and active_ratio >= self.active_bins_ratio:
            return True
        if peak_db < self.release_threshold_db and active_ratio < (self.active_bins_ratio / 2):
            return False
        return None


class RadioIQWorker:
    """Read UDP IQ samples and emit FFT data to the SocketIO clients."""

    def __init__(self, socketio: SocketIO, host: str = "0.0.0.0", port: int = 5005) -> None:
        self.socketio = socketio
        self.host = host
        self.port = port
        self.signal_detector = SignalDetector()

    def run(self) -> None:
        """Continuously receive UDP packets, compute the FFT, and broadcast the spectrum."""
        last_signal_state: Optional[bool] = None
        logger.info("Radio thread active in TC Generator.")

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((self.host, self.port))
            logger.info("UDP socket bound successfully on port %s", self.port)

            while True:
                try:
                    data, _ = sock.recvfrom(8192)
                    if not data:
                        continue

                    raw_samples = np.frombuffer(data, dtype=np.float32)
                    iq = raw_samples[0::2] + 1j * raw_samples[1::2]

                    fft_result = np.fft.fftshift(np.fft.fft(iq * np.hamming(len(iq))))
                    magnitude = 20 * np.log10(np.abs(fft_result) + 1e-10)
                    signal_state = self.signal_detector.detect(magnitude)

                    if signal_state is True and last_signal_state is not True:
                        logger.info("Signal detected.")
                        last_signal_state = True
                    elif signal_state is False and last_signal_state is not False:
                        logger.warning("Signal not detected.")
                        last_signal_state = False

                    self.socketio.emit("spectrum_data", {"db": magnitude.tolist()})
                except socket.timeout:
                    continue
                except Exception as exc:
                    logger.exception("Error processing packet: %s", exc)
                    continue
        except Exception as exc:
            logger.exception("Failed to bind UDP socket: %s", exc)
            return


if __name__ == "__main__":
    worker = RadioIQWorker(socketio=socketio)
    thread = threading.Thread(target=worker.run, daemon=True)
    thread.start()
    socketio.run(
        app,
        host="0.0.0.0",
        port=5000,
        debug=False,
        use_reloader=False,
        allow_unsafe_werkzeug=True,
    )