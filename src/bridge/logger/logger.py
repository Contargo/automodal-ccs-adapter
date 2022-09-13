from datetime import datetime, time
from pathlib import Path
from threading import Event, Thread

from bridge.sps.client import SpsClient
from bridge.sps.data import db_items


class Logger:
    def __init__(self, sps_client: SpsClient):
        self.sps_client = sps_client
        self.shutdown_event = Event()

        self.worker_logger: Thread = Thread(
            target=self.worker,
            args=(),
            name="Logger Worker",
            daemon=True,
        )

    def start(self) -> None:
        self.worker_logger.start()

    def worker(self) -> None:

        csv_head = "timestamp," + ",".join([dx.name for dx in db_items])
        file_path = Path("log.csv")
        file_path.write_text("")

        csv_file = file_path.open("a")
        csv_file.write(csv_head + "\n")
        while not self.shutdown_event.is_set():
            csv_line = (
                str(datetime.now())
                + ","
                + ",".join(
                    [
                        str(self.sps_client.read_value(dx.name, dx.type))
                        for dx in db_items
                    ]
                )
            )
            csv_file.write(csv_line + "\n")
            csv_file.flush()
            self.shutdown_event.wait(1)
        csv_file.close()

    def shutdown(self) -> None:
        self.shutdown_event.set()
