import requests
from requests import HTTPError
from faker import Faker
import getpass
import random
import hvac

KEYCLOAK_URL = 'http://localhost:8080/auth/'
REALM_NAME = 'master'

def get_secret_from_vault(token, secret_path, key):
    """Recupera un segreto da Vault."""
    client = hvac.Client(url='http://127.0.0.1:8200', token=token)
    read_response = client.secrets.kv.v2.read_secret_version(path=secret_path)
    return read_response['data']['data'][key]

def create_group(access_token, group_name):
    group_url = f"{KEYCLOAK_URL}admin/realms/{REALM_NAME}/groups"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    # Controlla se il gruppo esiste già
    response = requests.get(group_url, headers=headers)
    response.raise_for_status()
    groups = response.json()
    for group in groups:
        if group['name'] == group_name:
            print(f"Group '{group_name}' already exists")
            return group['id']

    # Se il gruppo non esiste, crealo
    group_data = {'name': group_name}
    response = requests.post(group_url, json=group_data, headers=headers)
    try:
        response.raise_for_status()
        print(f"Group '{group_name}' created successfully")
        # Fai una richiesta aggiuntiva per ottenere l'ID del gruppo appena creato
        response = requests.get(group_url, headers=headers)
        response.raise_for_status()
        groups = response.json()
        for group in groups:
            if group['name'] == group_name:
                return group['id']
    except HTTPError as e:
        print(f"Failed to create group '{group_name}'. Error: {e.response.text}")
        return None
    
def create_user(access_token, user_data):
    user_url = f"{KEYCLOAK_URL}admin/realms/{REALM_NAME}/users"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    response = requests.post(user_url, json=user_data, headers=headers)
    try:
        response.raise_for_status()
        return response.headers.get('Location').split('/')[-1]  # Get the ID of the created user
    except HTTPError as e:
        print(f"Failed to create user. Error: {e.response.text}")
        return None
    
def assign_user_to_group(access_token, user_id, group_id):
    assign_url = f"{KEYCLOAK_URL}admin/realms/{REALM_NAME}/users/{user_id}/groups/{group_id}"
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.put(assign_url, headers=headers)
    try:
        response.raise_for_status()
        print(f"User {user_id} assigned to group {group_id} successfully")
    except HTTPError as e:
        print(f"Failed to assign user {user_id} to group {group_id}. Error: {e.response.text}")

def create_oauth_client(access_token, client_data):
    client_url = f"{KEYCLOAK_URL}admin/realms/{REALM_NAME}/clients"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    response = requests.post(client_url, json=client_data, headers=headers)
    try:
        response.raise_for_status()
        print(f"OAuth client created successfully")
        return response.headers.get('Location').split('/')[-1]  # Get the ID of the created client
    except HTTPError as e:
        print(f"Failed to create OAuth client. Error: {e.response.text}")
        return None
    
def get_user_input():
    try:
        num_users = int(input("Inserisci il numero di utenti fittizi da creare: "))
    except ValueError:
        print("Si prega di inserire un numero valido.")
        return None, []

    group_names = []
    while True:
        group_name = input("Inserisci il nome del gruppo (lascia vuoto per terminare): ")
        if not group_name:
            break
        group_names.append(group_name)

    return num_users, group_names

def main():
    CLIENT_ID = 'admin-cli'
    GRANT_TYPE = 'password'

    token = getpass.getpass("Inserisci il Root Token di Vault: ")
    keycloak_user = get_secret_from_vault(token, 'application_secrets', 'keycloak_user') 
    keycloak_password = get_secret_from_vault(token, 'application_secrets', 'keycloak_password')

    if keycloak_user is None or keycloak_password is None:
        print("Impossibile recuperare le credenziali da Vault. Verifica la configurazione.")
        return

    token_url = f"{KEYCLOAK_URL}realms/{REALM_NAME}/protocol/openid-connect/token"
    token_data = {
        'client_id': CLIENT_ID,
        'username': keycloak_user,
        'password': keycloak_password,
        'grant_type': GRANT_TYPE,
    }

    response = requests.post(token_url, data=token_data)
    response.raise_for_status()
    access_token = response.json()['access_token']

    """
    # Parte relativa alla creazione del client OAuth
    client_data = {
        'clientId': 'client',
        'enabled': True,
        'publicClient': False,
        'redirectUris': ['http://localhost:8081/*'],
        'webOrigins': ['http://localhost:8081/'],
        'protocol': 'openid-connect',
        'standardFlowEnabled': True,
        'implicitFlowEnabled': False,
        'directAccessGrantsEnabled': True,
        'attributes': {
            'pkce.code.challenge.method': 'S256'
        },
        # Altre configurazioni...
    }

    client_id = create_oauth_client(access_token, client_data)

    if client_id:
        print(f"Client OAuth configurato con successo: {client_id}")
    else:
        print("Errore nella configurazione del client OAuth.")
    """

    num_users, group_names = get_user_input()

    if num_users is not None and group_names:
        group_ids = []
        for group_name in group_names:
            group_id = create_group(access_token, group_name)
            if group_id:
                group_ids.append(group_id)

        if len(group_ids) == len(group_names):
            faker = Faker()
            for _ in range(num_users):
                first_name = faker.first_name()
                last_name = faker.last_name()
                user_data = {
                    'username': faker.user_name(),
                    'enabled': True,
                    'email': faker.email(),
                    'firstName': first_name,
                    'lastName': last_name,
                    'credentials': [{
                        'type': 'password',
                        'value': 'password',
                        'temporary': False
                    }]
                }
                user_id = create_user(access_token, user_data)
                if user_id:
                    assign_user_to_group(access_token, user_id, random.choice(group_ids))
        else:
            print("Errore: Alcuni gruppi non possono essere creati o confermati.")
    else:
        print("Input non valido. Assicurati di inserire il numero di utenti e almeno un nome di gruppo.")

if __name__ == "__main__":
    main()