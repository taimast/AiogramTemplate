#!/bin/bash
psql -U postgres -d my_database -c "ALTER USER postgres WITH PASSWORD 'postgres';"