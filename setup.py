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


def create_secret_in_vault(token):
    """ Crea un segreto in Vault. """
    print("Creando un segreto in Vault...")
    client = hvac.Client(url='http://127.0.0.1:8200', token=token)
    client.secrets.kv.v2.create_or_update_secret(
        path='keycloak_postgres',
        secret={'password': 'YourSecurePassword'}
    )
    print("Segreto creato con successo.")

def get_vault_secret(token, secret_path, key):
    """Recupera un segreto da Vault."""
    print(f"Recuperando il segreto da Vault: {secret_path}")
    client = hvac.Client(url='http://127.0.0.1:8200', token=token)
    read_response = client.secrets.kv.v2.read_secret_version(path=secret_path)
    return read_response['data']['data'][key]

def set_env_variables(postgres_password):
    """ Imposta le variabili d'ambiente per le credenziali. """
    keycloak_user = input("Inserisci l'username per l'amministratore Keycloak: ")
    keycloak_password = getpass.getpass("Inserisci la password per l'amministratore Keycloak: ")

    os.environ['POSTGRES_PASSWORD'] = postgres_password
    os.environ['KEYCLOAK_USER'] = keycloak_user
    os.environ['KEYCLOAK_PASSWORD'] = keycloak_password

def create_docker_compose():
    """ Crea il file docker-compose.yml. """
    print("Creando il file docker-compose.yml...")
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

    with open('keycloak-postgres.yml', 'w') as file:
        file.write(docker_compose_content)
    print("File docker-compose.yml creato con successo.")

def main():
    """ Funzione principale per eseguire il setup. """
    if not is_vault_running():
        print("Vault non è in esecuzione. Per favore esegui il comando 'vault server -dev' e riprova.")
        return
    if not is_docker_running():
        print("Docker non è in esecuzione. Assicurati che Docker sia avviato e riprova.")
        return

    token = input("Inserisci il Root Token di Vault: ")
    os.environ['VAULT_ADDR'] = 'http://127.0.0.1:8200'
    os.environ['VAULT_TOKEN'] = token

    create_secret_in_vault(token)
    postgres_password = get_vault_secret(token, 'keycloak_postgres', 'password')
    
    set_env_variables(postgres_password)
    create_docker_compose()

    print("Avviando i servizi con Docker Compose...")
    subprocess.run(["docker-compose", "-f", "keycloak-postgres.yml", "up", "-d"])
    print("Servizi avviati.")
    print("Setup completato. Connettiti su http://localhost:8080")

if __name__ == "__main__":
    main()
