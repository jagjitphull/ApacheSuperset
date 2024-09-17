#!/bin/bash

rm -rf ~/superset
sudo dnf -y remove postgresql postgresql-server
sudo rm -rf /var/lib/pgsql/
