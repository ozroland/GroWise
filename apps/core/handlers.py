import logging
from django.utils.timezone import now


class DatabaseLogHandler(logging.Handler):
    def emit(self, record):
        from .models import Log 
        log_entry = Log(
            level=record.levelname,
            message=self.format(record),
            created_at=now(),
        )
        log_entry.save()