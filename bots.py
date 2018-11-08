#!/usr/bin/env python
import os


if __name__ == '__main__':

    os.environ.setdefault('SETTINGS', 'settings.yml,secrets.yml')

    try:
        from trading_bots.core.management import cli

    except ImportError as exc:
        raise ImportError(
            "Couldn't import Trading-Bots. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    cli()
