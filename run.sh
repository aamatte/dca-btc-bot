#!/bin/bash
# Script to run the bot indefinitely, recovering from possible crashes
# Set boot interval to 10 minutes refresh, and recovering time also to 10m
while :
do
	python bots.py loop buda --interval 900
	echo "Restarting in 10min.."
	sleep 10m
done

