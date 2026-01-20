import logging

logger = logging.getLogger(__name__)


def main() -> bool:
    logging.basicConfig(level=logging.INFO)

    logger.info('running')

    return True
