#!/bin/sh

# Inizializza e avvia PostgreSQL come utente 'postgres'
su postgres -c "initdb /var/lib/postgresql/data"
su postgres -c "pg_ctl -D /var/lib/postgresql/data start"

# Aspetta che PostgreSQL sia completamente avviato
sleep 5

# Impostazioni di Keycloak (modifica secondo necessità)
read -p "Enter admin username: " KEYCLOAK_ADMIN
read -s -p "Enter admin password: " KEYCLOAK_ADMIN_PASSWORD
echo

# Configura il database per Keycloak
su postgres -c "createdb keycloak"
su postgres -c "createuser $KEYCLOAK_ADMIN"
su postgres -c "psql -c \"ALTER USER $KEYCLOAK_ADMIN WITH ENCRYPTED PASSWORD '$KEYCLOAK_ADMIN_PASSWORD';\""
su postgres -c "psql -c \"GRANT ALL PRIVILEGES ON DATABASE keycloak TO $KEYCLOAK_ADMIN;\""
su postgres -c "psql -c \"ALTER USER $KEYCLOAK_ADMIN WITH SUPERUSER;\""

export KEYCLOAK_ADMIN
export KEYCLOAK_ADMIN_PASSWORD

# Avvia Keycloak in background
/opt/keycloak-23.0.1/bin/kc.sh start-dev --db=postgres --db-username=$KEYCLOAK_ADMIN --db-password=$KEYCLOAK_ADMIN_PASSWORD --db-url=jdbc:postgresql://localhost/keycloak &

# Attendi che Keycloak sia completamente avviato
while ! nc -z localhost 8080; do   
  sleep 10 # aspetta 1 secondo prima di controllare di nuovo
done

# Ora Keycloak è avviato, esegui lo script Python
python3 /main.py

