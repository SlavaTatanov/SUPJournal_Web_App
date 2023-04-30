#!/bin/bash

read -r -e -p "Логин БД: " DB_USERNAME_INP
read -r -e -p "Пароль БД: " DB_PASSWORD_INP

export DB_USERNAME="$DB_USERNAME_INP"
export DB_PASSWORD="$DB_PASSWORD_INP"

flask --app SUPJournal run
