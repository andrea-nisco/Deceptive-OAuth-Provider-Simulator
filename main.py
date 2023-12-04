from faker import Faker
import os
import requests
import json
from requests.exceptions import HTTPError
import random

# Configura l'URL del server Keycloak
KEYCLOAK_URL = "http://0.0.0.0:8080"  # Assicurati che questo indirizzo sia corretto
KEYCLOAK_REALM = "master"
KEYCLOAK_CLIENT_ID = "admin-cli"
KEYCLOAK_GRANT_TYPE = "password"

# Recupera le credenziali dell'amministratore dalle variabili d'ambiente
KEYCLOAK_ADMIN_USER = os.environ.get("KEYCLOAK_ADMIN", "admin")  # Default a "admin" se non impostato
KEYCLOAK_ADMIN_PASSWORD = os.environ.get("KEYCLOAK_ADMIN_PASSWORD", "password")  # Default a "password" se non impostato

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

# Funzione per generare dati casuali per un utente con email reale
def generate_random_user_data():
    fake = Faker()

    # Genera un username per l'account
    username = fake.user_name()

    # Genera un username separato per l'email
    email_username = fake.user_name()
    
    # Dizionario di provider di email fittizi
    fake_email_providers = ['gmail.com', 'yahoo.com', 'hotmail.com', 'aol.com', 'hotmail.co.uk', 'hotmail.fr', 'msn.com', 'yahoo.fr', 'wanadoo.fr', 'orange.fr', 
                            'comcast.net', 'yahoo.co.uk', 'yahoo.com.br', 'yahoo.co.in', 'live.com', 'rediffmail.com', 'free.fr', 'gmx.de', 'web.de', 'yandex.ru', 
                            'ymail.com', 'libero.it', '	outlook.com', '	uol.com.br', '	bol.com.br', 'mail.ru', 'cox.net', 'hotmail.it', 'sbcglobal.net', 'sfr.fr', 
                            'live.fr', 'verizon.net', '	live.co.uk', 'googlemail.com', 'yahoo.es', 'ig.com.br', 'live.nl', 'bigpond.com', 'terra.com.br', 'yahoo.it', 
                            'neuf.fr', 'yahoo.de', 'alice.it', 'rocketmail.com', 'att.net', 'laposte.net', 'facebook.com', 'bellsouth.net', 'yahoo.in', 'hotmail.es', 
                            'charter.net', 'yahoo.ca', 'yahoo.com.au', 'rambler.ru', 'hotmail.de', 'tiscali.it', 'shaw.ca', 'yahoo.co.jp', 'sky.com', 'earthlink.net', 
                            'optonline.net', 'freenet.de', 't-online.de', 'aliceadsl.fr', 'virgilio.it', 'home.nl', 'qq.com', 'telenet.be', 'me.com', 'yahoo.com.ar', 
                            'tiscali.co.uk', 'yahoo.com.mx', 'voila.fr', 'gmx.net', 'mail.com', 'planet.nl', 'tin.it', 'live.it', 'ntlworld.com', 'arcor.de', 'yahoo.co.id', 
                            'frontiernet.net', 'hetnet.nl', 'live.com.au', 'yahoo.com.sg', 'zonnet.nl', 'club-internet.fr', 'juno.com', 'optusnet.com.au', 'blueyonder.co.uk', 
                            'bluewin.ch', 'skynet.be', 'sympatico.ca', 'windstream.net', 'mac.com', 'centurytel.net', '	chello.nl', 'live.ca', 'aim.com', 'bigpond.net.au', 'proton.me']
    
    # Scegli un provider email casuale dal dizionario
    email_provider = random.choice(fake_email_providers)
    email = f"{email_username}@{email_provider}"

    # Genera una password
    password = fake.password()

    return username, email, password

# Funzione per creare un nuovo utente
def create_user(token, username, email, password):
    try:
        url = f"{KEYCLOAK_URL}/admin/realms/{KEYCLOAK_REALM}/users"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        data = {
            "username": username,
            "email": email,
            "enabled": True,
            "credentials": [{"type": "password", "value": password, "temporary": False}]
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        return response.status_code
    except requests.exceptions.RequestException as e:
        #print(f"Errore durante la creazione dell'utente: {e}")
        return None
    
# Funzione per creare n utenti casuali
def create_n_random_users(n):
    token = get_token()
    if not token:
        print("Impossibile ottenere il token di accesso.")
        return

    utenti_creati = 0
    while utenti_creati < n:
        username, email, password = generate_random_user_data()
        status_code = create_user(token, username, email, password)
        if status_code == 201:
            utenti_creati += 1
            print(f"Utente {username} creato con successo.")

# Funzione per ottenere tutti gli utenti
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
    try:
        response.raise_for_status()
        print(f"User {user_id} assigned to group {group_id} successfully")
    except HTTPError as e:
        print(f"Failed to assign user {user_id} to group {group_id}. Error: {e.response.text}")

# Funzione per creare gruppi e assegnare utenti in modo casuale
def create_groups_and_assign_users(group_names, num_users_to_assign):
    token = get_token()
    if not token:
        print("Impossibile ottenere il token di accesso.")
        return

    group_ids = {}
    for group_name in group_names:
        group_id = create_group(token, group_name)
        if group_id:
            group_ids[group_name] = group_id

    users = get_all_users(token)
    if users is None:
        return

    # Assicurati che il numero di utenti da assegnare non sia maggiore del totale disponibile
    num_users_to_assign = min(num_users_to_assign, len(users))

    # Mescola casualmente la lista degli utenti
    random.shuffle(users)

    # Dizionario per tenere traccia della distribuzione degli utenti nei gruppi
    group_distribution = {group_name: 0 for group_name in group_names}

    # Assegna gli utenti ai gruppi in modo casuale
    for i in range(num_users_to_assign):
        user = users[i]
        user_id = user['id']
        group_name, group_id = random.choice(list(group_ids.items()))
        assign_user_to_group(token, user_id, group_id)
        group_distribution[group_name] += 1

    # Stampa la distribuzione degli utenti nei gruppi
    for group_name, count in group_distribution.items():
        print(f"{group_name}: {count} utenti")

# Funzione per mostrare il menu e gestire le scelte dell'utente
def main_menu():
    while True:
        print("\nMenu:")
        print("3. Crea gruppi e assegna utenti")
        print("2. Crea n utenti casuali")
        print("1. Crea un singolo utente")
        print("0. Esci")
        scelta = input("Inserisci la tua scelta: ")

        if scelta == "3":
            token = get_token()
            if token:
                all_users = get_all_users(token)
                if all_users:
                    total_users = len(all_users)
                    print(f"Numero totale di utenti nel database: {total_users}")
                    while True:  # Aggiungi un ciclo per controllare l'input dell'utente
                        num_users_to_assign = int(input("Quanti utenti vuoi distribuire nei gruppi?: "))
                        if num_users_to_assign <= total_users:
                            break  # L'input è valido, esci dal ciclo
                        else:
                            print(f"Errore: hai inserito un numero maggiore del totale di utenti disponibili ({total_users}). Riprova.")

                    num_gruppi = int(input("Inserisci il numero di gruppi da creare: "))
                    group_names = []
                    for i in range(num_gruppi):
                        group_name = input(f"Inserisci il nome per il gruppo {i+1}: ")
                        group_names.append(group_name)
                    create_groups_and_assign_users(group_names, num_users_to_assign)
            else:
                print("Impossibile ottenere il token di accesso.")

        elif scelta == "2":
            numero_utenti = int(input("Con quanti utenti vuoi popolare il database?: "))
            create_n_random_users(numero_utenti)
        
        elif scelta == "1":
            username = input("Inserisci il nome utente: ")
            email = input("Inserisci l'email: ")
            password = input("Inserisci la password: ")
            token = get_token()
            if token:
                status_code = create_user(token, username, email, password)
                if status_code == 201:
                    print("Utente creato con successo.")
                else:
                    print(f"Errore nella creazione dell'utente. Codice di risposta: {status_code}")
            else:
                print("Impossibile ottenere il token di accesso.")

        elif scelta == "0":
            break
        else:
            print("Scelta non valida.")

# Esecuzione del menu principale
if __name__ == "__main__":
    main_menu()