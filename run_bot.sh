#!/bin/sh
export LC_ALL=en_US.UTF-8
#rm *.db
#rm opportune_bot.log
./db/init_database.py
./app.py
