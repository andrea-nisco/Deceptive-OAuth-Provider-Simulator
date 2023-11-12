import requests
from requests import HTTPError
from faker import Faker
import random

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

KEYCLOAK_URL = 'http://localhost:8080/auth/'
REALM_NAME = 'master'
CLIENT_ID = 'admin-cli'
USERNAME = 'admin'
PASSWORD = 'Pa55w0rd'
GRANT_TYPE = 'password'
CLIENT_SECRET = 'JJcMHwA7Waq0g6DiGTCjLc9pVi90kfAm'

# Ottieni il token di accesso
token_url = f"{KEYCLOAK_URL}realms/{REALM_NAME}/protocol/openid-connect/token"
token_data = {
    'client_id': CLIENT_ID,
    'username': USERNAME,
    'password': PASSWORD,
    'grant_type': GRANT_TYPE,
}

if CLIENT_SECRET:
    token_data['client_secret'] = CLIENT_SECRET

response = requests.post(token_url, data=token_data)
response.raise_for_status()
access_token = response.json()['access_token']

group_names = ['Group1', 'Group2', 'Group3', 'Test']
group_ids = []
for group_name in group_names:
    group_id = create_group(access_token, group_name)
    if group_id:
        group_ids.append(group_id)

if len(group_ids) == len(group_names):
    # Generazione e creazione di utenti fittizi
    faker = Faker()
    num_users = 10

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
    print("Error: Some groups could not be created or confirmed.")