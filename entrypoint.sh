#!/bin/sh

# Controlla e crea il volume per PostgreSQL se non esiste
if [ ! -d "/var/lib/postgresql/data" ]; then
    mkdir -p /var/lib/postgresql/data
fi

# Controlla e crea il volume per Keycloak se non esiste
if [ ! -d "/opt/keycloak-23.0.1/standalone/data" ]; then
    mkdir -p /opt/keycloak-23.0.1/standalone/data
fi

# Assegna i permessi corretti per i volumi
chown -R postgres:postgres /var/lib/postgresql/data
chown -R postgres:postgres /opt/keycloak-23.0.1/standalone/data

# Inizializza e avvia PostgreSQL come utente 'postgres'
su postgres -c "initdb /var/lib/postgresql/data"
su postgres -c "pg_ctl -D /var/lib/postgresql/data start"

# Aspetta che PostgreSQL sia completamente avviato
until su postgres -c "pg_isready -d keycloak"; do
  echo "Aspettando che PostgreSQL sia pronto..."
  sleep 20
done

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
  echo "Aspettando che Keycloak sia pronto..."
  sleep 1
done

# Ora Keycloak è avviato, esegui lo script Python
python3 /main.py
