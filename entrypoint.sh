#!/bin/sh

# Percorsi dei file per memorizzare le credenziali
ADMIN_CREDENTIALS_FILE="/opt/keycloak-23.0.1/credentials/admin_credentials.txt"

# Chiedi la chiave di cifratura all'utente
echo "Inserisci la chiave di cifratura:"
read -s ENCRYPTION_KEY

# Controlla se il file delle credenziali esiste e decifrane il contenuto
if [ -f "$ADMIN_CREDENTIALS_FILE" ]; then
    read KEYCLOAK_ADMIN KEYCLOAK_ADMIN_PASSWORD < <(openssl enc -aes-256-cbc -d -a -pbkdf2 -iter 10000 -in $ADMIN_CREDENTIALS_FILE -pass pass:$ENCRYPTION_KEY)
fi

# Controlla e crea il volume per PostgreSQL se non esiste
if [ ! -d "/var/lib/postgresql/data" ]; then
    mkdir -p /var/lib/postgresql/data > /dev/null 2>&1
fi

# Controlla e crea il volume per Keycloak se non esiste
if [ ! -d "/opt/keycloak-23.0.1/standalone/data" ]; then
    mkdir -p /opt/keycloak-23.0.1/standalone/data > /dev/null 2>&1
fi

# Assegna i permessi corretti per i volumi
chown -R postgres:postgres /var/lib/postgresql/data > /dev/null 2>&1
chown -R postgres:postgres /opt/keycloak-23.0.1/standalone/data > /dev/null 2>&1

# Inizializza e avvia PostgreSQL come utente 'postgres'
su postgres -c "initdb /var/lib/postgresql/data" > /dev/null 2>&1
su postgres -c "pg_ctl -D /var/lib/postgresql/data start" > /dev/null 2>&1

echo "Aspettando che PostgreSQL sia pronto..."
# Aspetta che PostgreSQL sia completamente avviato
until su postgres -c "pg_isready -d keycloak"; do
  sleep 1
done

# Verifica se le credenziali di amministratore esistono
if [ ! -f "$ADMIN_CREDENTIALS_FILE" ]; then
    # Chiede all'utente di inserire le credenziali
    read -p "Inserire admin username (will be saved encrypted): " KEYCLOAK_ADMIN
    read -s -p "Inserire admin password (will be saved encrypted): " KEYCLOAK_ADMIN_PASSWORD
    echo

    # Cifra e salva le credenziali per i successivi avvii
    echo "$KEYCLOAK_ADMIN $KEYCLOAK_ADMIN_PASSWORD" | openssl enc -aes-256-cbc -a -salt -pbkdf2 -iter 10000 -pass pass:$ENCRYPTION_KEY > $ADMIN_CREDENTIALS_FILE
    chmod 600 $ADMIN_CREDENTIALS_FILE

    # Configura il database per Keycloak
    su postgres -c "createdb keycloak" > /dev/null 2>&1
    su postgres -c "createuser $KEYCLOAK_ADMIN" > /dev/null 2>&1
    su postgres -c "psql -c \"ALTER USER $KEYCLOAK_ADMIN WITH ENCRYPTED PASSWORD '$KEYCLOAK_ADMIN_PASSWORD';\"" > /dev/null 2>&1
    su postgres -c "psql -c \"GRANT ALL PRIVILEGES ON DATABASE keycloak TO $KEYCLOAK_ADMIN;\"" > /dev/null 2>&1
    su postgres -c "psql -c \"ALTER USER $KEYCLOAK_ADMIN WITH SUPERUSER;\"" > /dev/null 2>&1
else
    # Legge le credenziali salvate e le decifra
    openssl enc -aes-256-cbc -d -a -pbkdf2 -iter 10000 -in $ADMIN_CREDENTIALS_FILE -pass pass:$ENCRYPTION_KEY | read KEYCLOAK_ADMIN KEYCLOAK_ADMIN_PASSWORD
fi

export KEYCLOAK_ADMIN 
export KEYCLOAK_ADMIN_PASSWORD

# Avvia Keycloak in background
/opt/keycloak-23.0.1/bin/kc.sh start-dev --db=postgres --db-username=$KEYCLOAK_ADMIN --db-password=$KEYCLOAK_ADMIN_PASSWORD --db-url=jdbc:postgresql://localhost/keycloak > /dev/null 2>&1 &

echo "Aspettando che Keycloak sia pronto..."
# Attendi che Keycloak sia completamente avviato
while ! nc -z localhost 8080; do   
  sleep 1
done

# Verifica delle credenziali prima di eseguire main.py

#read -p "Verify your admin username to start the service: " INPUT_ADMIN
read -p "Verifica il tuo admin username per avviare il servizio: " INPUT_ADMIN
#read -s -p "Verify your admin password to start the service: " INPUT_ADMIN_PASSWORD
read -s -p "Verifica la tua admin password per avviare il servizio: " INPUT_ADMIN_PASSWORD

echo

if [ "$INPUT_ADMIN" = "$KEYCLOAK_ADMIN" ] && [ "$INPUT_ADMIN_PASSWORD" = "$KEYCLOAK_ADMIN_PASSWORD" ]; then
    # Attiva l'ambiente virtuale prima di eseguire main.py
    . /opt/venv/bin/activate
    python /main.py
    deactivate
else
    # Credenziali errate, non eseguire main.py
    echo "Credenziali errate, riprova."
fi
