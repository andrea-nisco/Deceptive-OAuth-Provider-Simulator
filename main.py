import requests
from faker import Faker
import os

# URL base e nome del realm di Keycloak
KEYCLOAK_URL = 'http://0.0.0.0:8080/auth/'
REALM_NAME = 'master'

# Credenziali amministratore da variabili d'ambiente
KEYCLOAK_ADMIN = os.environ['KEYCLOAK_ADMIN']
KEYCLOAK_ADMIN_PASSWORD = os.environ['KEYCLOAK_ADMIN_PASSWORD']

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


# Generatore di dati casuali
faker = Faker()

# Numero di utenti da generare
num_users = int(input("Con quanti utenti vuoi popolare il database? "))

# Inserimento dei nomi dei gruppi e creazione dei gruppi
group_ids = []
for _ in range(int(input("Quanti gruppi vuoi creare? "))):
    group_name = input("Scrivi nome gruppo: ")
    group_id = create_group(KEYCLOAK_ADMIN, KEYCLOAK_ADMIN_PASSWORD, group_name)
    if group_id:
        group_ids.append(group_id)

# Creazione di utenti casuali e assegnazione a gruppi
for _ in range(num_users):
    username = faker.user_name()
    email = faker.email()
    user_data = {
        "username": username,
        "email": email,
        "enabled": True,
        "emailVerified": True
    }
    user_id = create_user(KEYCLOAK_ADMIN, KEYCLOAK_ADMIN_PASSWORD, user_data)
    if user_id and group_ids:
        assign_user_to_group(KEYCLOAK_ADMIN, KEYCLOAK_ADMIN_PASSWORD, user_id, faker.random.choice(group_ids))

print("Popolamento del database completato.")

