#!/bin/bash
rm -Rf output/*
rm -Rf temp/*
sudo bash /usr/local/bin/cooler-control on
docker compose up
sudo bash /usr/local/bin/cooler-control off
