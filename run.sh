#!/bin/bash
trap 'echo "abort signal received, exiting..."; exit 0' SIGTERM SIGQUIT SIGINT

while true; do
  pipenv run ./bots.py run buda
  sleep $(($INVESTMENT_INTERVAL_HOURS * 60 * 60)) & wait $!
done