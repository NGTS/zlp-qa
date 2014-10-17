import logging
import sys
import structlog
import datetime

fmt = '%(message)s'
logging.basicConfig(level=logging.DEBUG, format=fmt, stream=sys.stdout)

def add_timestamp(_, __, event_dict):
    event_dict['timestamp'] = str(datetime.datetime.utcnow())
    return event_dict

def add_logging_level(_, method, event_dict):
    if method == 'warn':
        name = 'warning'
    else:
        name = method

    event_dict['level'] = name
    event_dict['method'] = method
    return event_dict

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        add_timestamp,
        add_logging_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)


def get_logger(filename):
    return structlog.get_logger().bind(source=filename,
                                       pipeline_stage='quality_assessment')
