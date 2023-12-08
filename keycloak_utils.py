import requests  # Per eseguire richieste HTTP a Keycloak
from requests.exceptions import HTTPError  # Per gestire le eccezioni HTTP
import jwt  # Libreria PyJWT per la decodifica dei token JWT
import time  # Per gestire il tempo (es. confrontare timestamp)
import json  # Per la serializzazione/deserializzazione dei dati JSON
from tqdm import tqdm

from config import *
from user import *

# Funzione per ottenere il token di accesso
def get_token():
    try:
        url = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token"
        data = {
            "client_id": KEYCLOAK_CLIENT_ID,
            "username": KEYCLOAK_ADMIN_USER,
            "password": KEYCLOAK_ADMIN_PASSWORD,
            "grant_type": KEYCLOAK_GRANT_TYPE
        }
        response = requests.post(url, data=data)
        response.raise_for_status()
        token = response.json()["access_token"]
        return token
    except requests.exceptions.RequestException as e:
        print(f"Errore durante l'ottenimento del token: {e}")
        return None

# Funzione per rinnovare il token di accesso se scade
def token_scaduto(token):
    try:
        # Decodifica il token per ottenere il payload
        # Non è necessario verificare la firma del token in questo caso
        payload = jwt.decode(token, options={"verify_signature": False})

        # Ottieni il timestamp di scadenza dal payload
        exp = payload.get("exp")

        # Confronta il timestamp di scadenza con il tempo corrente
        # time.time() restituisce il tempo corrente in secondi dal 1 gennaio 1970
        if exp is not None and exp < time.time():
            return True  # Il token è scaduto
        return False  # Il token non è scaduto
    except jwt.DecodeError:
        print("Errore nella decodifica del token.")
        return True  # Se c'è un errore nella decodifica, assumi che il token sia scaduto

# Funzione per creare un nuovo client
def create_oauth_client(access_token, client_data):
    client_url = f"{KEYCLOAK_URL}/admin/realms/{KEYCLOAK_REALM}/clients"
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

# Funzione per creare un nuovo utente
def create_user(token, user):
    try:
        url = f"{KEYCLOAK_URL}/admin/realms/{KEYCLOAK_REALM}/users"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        data = {
            "username": user.username,
            "email": user.email,
            "enabled": True,
            "credentials": [{"type": "password", "value": user.password, "temporary": False}],
            "firstName": user.first_name,
            "lastName": user.last_name,
            "attributes": {
                "Data Di Nascita": user.birth_date,
                "Genere": user.gender,
                "Luogo Di Nascita": user.birth_place,
                "Codice Fiscale": user.cf
            }
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        return response.status_code
    
    # Rimuovere le print commentate per eseguire debug
    except requests.exceptions.HTTPError as e:
        #print(f"HTTP Error: {e}")
        return None
    except requests.exceptions.ConnectionError as e:
        #print(f"Connection Error: {e}")
        return None
    except requests.exceptions.Timeout as e:
        #print(f"Timeout Error: {e}")
        return None
    except requests.exceptions.RequestException as e:
        #print(f"Errore Generico: {e}")
        return None
    
# Funzione per creare n utenti casuali
def create_n_random_users(n, fake):
    token = get_token()
    if not token:
        print("Impossibile ottenere il token di accesso.")
        return

    created = 0
    attempts = 0
    max_attempts = 5

    with tqdm(total=n, desc="Creazione utenti", unit="utente") as pbar:
        while created < n:
            user = generate_random_user_data(fake)

            # Rinnova il token se necessario
            if token_scaduto(token):
                token = get_token()
                if not token:
                    print("Impossibile rinnovare il token di accesso.")
                    break
            
            status_code = create_user(token, user)

            if status_code == 201:
                created += 1
                attempts = 0
                pbar.update(1)
            else:
                # Rimuovere le print commentate per eseguire debug
                attempts += 1
                if attempts >= max_attempts:
                    #print(f"Massimo numero di tentativi raggiunto per l'utente {user.username}")
                    break
                sleep_time = 0.1 ** attempts
                #print(f"Ritentare dopo {sleep_time} secondi")
                time.sleep(sleep_time)

    print(f"Utenti creati: {created}/{n}")

def delete_user(token, user_id):
    delete_url = f"{KEYCLOAK_URL}/admin/realms/{KEYCLOAK_REALM}/users/{user_id}"
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.delete(delete_url, headers=headers)

    # Rimuovere le print commentate per eseguire debug
    try:
        response.raise_for_status()
        # print(f"User {user_id} deleted successfully")
    except HTTPError as e:
        # print(f"Failed to delete user {user_id}. Error: {e.response.text}")
        return None

def get_all_users(token):
    users = []
    users_url = f"{KEYCLOAK_URL}/admin/realms/{KEYCLOAK_REALM}/users"
    headers = {"Authorization": f"Bearer {token}"}

    page = 0
    while True:
        params = {'first': page * 100, 'max': 100}  # 100 è il numero di utenti per pagina
        response = requests.get(users_url, headers=headers, params=params)
        if response.status_code == 200:
            page_users = response.json()
            if not page_users:
                break  # Interrompe il ciclo se non ci sono più utenti
            # Filtra l'utente "admin"
            page_users = [user for user in page_users if user['username'] != KEYCLOAK_ADMIN_USER]
            users.extend(page_users)
            page += 1
        else:
            print("Errore nell'ottenere gli utenti.")
            return None

    return users

# Funzione che crea un singolo gruppo
def create_group(access_token, group_name):
    group_url = f"{KEYCLOAK_URL}/admin/realms/{KEYCLOAK_REALM}/groups"
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

# Funzione per assegnare un utente ad un gruppo
def assign_user_to_group(access_token, user_id, group_id):
    assign_url = f"{KEYCLOAK_URL}/admin/realms/{KEYCLOAK_REALM}/users/{user_id}/groups/{group_id}"
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.put(assign_url, headers=headers)
    
    # Rimuovere le print commentate per eseguire debug
    try:
        response.raise_for_status()
        #print(f"User {user_id} assigned to group {group_id} successfully")
    except HTTPError as e:
        #print(f"Failed to assign user {user_id} to group {group_id}. Error: {e.response.text}")
        return None