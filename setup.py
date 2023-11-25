import os
import hvac
import getpass
import subprocess
import requests

def is_vault_running():
    """ Verifica se Vault è in esecuzione. """
    try:
        response = requests.get('http://127.0.0.1:8200/v1/sys/health')
        return response.status_code == 200
    except requests.ConnectionError:
        return False

def is_docker_running():
    """ Verifica se Docker è in esecuzione. """
    try:
        subprocess.run(["docker", "info"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

def save_secrets_in_vault(token):
    """ Salva i dati sensibili in Vault. """
    client = hvac.Client(url='http://127.0.0.1:8200', token=token)
    
    keycloak_user = input("Inserisci l'username per l'amministratore Keycloak: ")
    keycloak_password = getpass.getpass("Inserisci la password per l'amministratore Keycloak: ")
    postgres_password = getpass.getpass("Inserisci la password per l'utente PostgreSQL: ")

    client.secrets.kv.v2.create_or_update_secret(
        path='application_secrets',
        secret={
            'keycloak_user': keycloak_user,
            'keycloak_password': keycloak_password,
            'postgres_password': postgres_password
        }
    )

def get_secret_from_vault(token, secret_path, key):
    """Recupera un segreto da Vault."""
    client = hvac.Client(url='http://127.0.0.1:8200', token=token)
    read_response = client.secrets.kv.v2.read_secret_version(path=secret_path)
    return read_response['data']['data'][key]

def create_docker_compose(token):
    """ Crea il file docker-compose.yml sostituendo le variabili con i segreti da Vault. """
    docker_compose_content = """version: '3'
volumes:
  postgres_data:
      driver: local

services:
  postgres:
      image: postgres
      volumes:
        - postgres_data:/var/lib/postgresql/data
      environment:
        POSTGRES_DB: keycloak
        POSTGRES_USER: keycloak
        POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
  keycloak:
      image: quay.io/keycloak/keycloak:legacy
      environment:
        DB_VENDOR: POSTGRES
        DB_ADDR: postgres
        DB_DATABASE: keycloak
        DB_USER: keycloak
        DB_SCHEMA: public
        DB_PASSWORD: ${POSTGRES_PASSWORD}
        KEYCLOAK_USER: ${KEYCLOAK_USER}
        KEYCLOAK_PASSWORD: ${KEYCLOAK_PASSWORD}
      ports:
        - 8080:8080
      depends_on:
        - postgres
"""

    client = hvac.Client(url='http://127.0.0.1:8200', token=token)
    keycloak_user = get_secret_from_vault(token, 'application_secrets', 'keycloak_user')
    keycloak_password = get_secret_from_vault(token, 'application_secrets', 'keycloak_password')
    postgres_password = get_secret_from_vault(token, 'application_secrets', 'postgres_password')

    os.environ['POSTGRES_PASSWORD'] = postgres_password
    os.environ['KEYCLOAK_USER'] = keycloak_user
    os.environ['KEYCLOAK_PASSWORD'] = keycloak_password

    with open('keycloak-postgres.yml', 'w') as file:
        file.write(docker_compose_content)
    print("File docker-compose.yml creato con successo.")

def main():
    if not is_vault_running():
        print("Vault non è in esecuzione. Per favore esegui il comando 'vault server -dev' e riprova.")
        return
    if not is_docker_running():
        print("Docker non è in esecuzione. Assicurati che Docker sia avviato e riprova.")
        return

    token = getpass.getpass("Inserisci il Root Token di Vault: ")
    os.environ['VAULT_ADDR'] = 'http://127.0.0.1:8200'
    os.environ['VAULT_TOKEN'] = token
    
    save_secrets_in_vault(token)
    
    create_docker_compose(token)
    
    postgres_password = get_secret_from_vault(token, 'application_secrets', 'postgres_password')
    
    print("Avviando i servizi con Docker Compose...")
    subprocess.run(["docker-compose", "-f", "keycloak-postgres.yml", "up", "-d"])
    print("Servizi avviati.")
    print("Setup completato. Connettiti su http://localhost:8080")

if __name__ == "__main__":
    main()
