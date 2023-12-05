from faker import Faker
from tqdm import tqdm
import os
import requests
import json
from requests.exceptions import HTTPError
import random
import datetime
import jwt  # Libreria PyJWT
import time

# Configura l'URL del server Keycloak
KEYCLOAK_URL = "http://0.0.0.0:8080"  # Assicurati che questo indirizzo sia corretto
KEYCLOAK_REALM = "master"
KEYCLOAK_CLIENT_ID = "admin-cli"
KEYCLOAK_GRANT_TYPE = "password"

# Recupera le credenziali dell'amministratore dalle variabili d'ambiente
KEYCLOAK_ADMIN_USER = os.environ.get("KEYCLOAK_ADMIN", "admin")  # Default a "admin" se non impostato
KEYCLOAK_ADMIN_PASSWORD = os.environ.get("KEYCLOAK_ADMIN_PASSWORD", "password")  # Default a "password" se non impostato

# Classe User
class User:
    def __init__(self, username, email, password, first_name, last_name, birth_date, gender, birth_place, cf):
        self.username = username
        self.email = email
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.birth_date = birth_date
        self.gender = gender
        self.birth_place = birth_place
        self.cf = cf

def clear_screen():
    # Windows
    if os.name == 'nt':
        _ = os.system('cls')
    # MacOS/Linux
    else:
        _ = os.system('clear')

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

def generate_username(first_name, last_name, birth_date, fake):
    birth_year = birth_date.strftime("%Y")
    birth_month_day = birth_date.strftime("%m%d")
    random_book_title = fake.word().lower()
    random_game = fake.word().lower()
    random_color = fake.color_name().lower().replace(" ", "")
    random_city = fake.city().lower().replace(" ", "")
    random_country = fake.country().lower().replace(" ", "")

    # Definisci 30 strategie diverse per la creazione dell'username
    strategies = [
        lambda: f"{first_name}.{last_name}",
        lambda: f"{last_name}_{first_name}",
        lambda: f"{first_name[0]}{last_name}{birth_year}",
        lambda: f"{first_name}{birth_month_day}",
        lambda: f"{last_name[:3]}{first_name[:2]}{birth_year[-2:]}",
        lambda: f"{random_book_title}{last_name[:3]}",
        lambda: f"{first_name}_{random_game}",
        lambda: f"{random_game}{birth_year}",
        lambda: f"{random_color}{last_name[0]}{birth_year[-2:]}",
        lambda: f"{first_name}{random_country[:3]}",
        lambda: f"{random_city}_{first_name[0]}{last_name[0]}",
        lambda: f"{birth_year}{random_book_title}",
        lambda: f"{last_name}_{random_color}",
        lambda: f"{random_game[0:3]}_{birth_month_day}",
        lambda: f"{last_name[0:3]}_{random_city}",
        lambda: f"{random_country}_{birth_year}",
        lambda: f"{birth_month_day}_{random_game}",
        lambda: f"{random_color}{birth_year}",
        lambda: f"{first_name}_{random_country[:3]}",
        lambda: f"{last_name[0]}{random_city[0:3]}{birth_year}",
        lambda: f"{random_book_title[0:3]}_{random_country[0:3]}",
        lambda: f"{first_name[0]}{random_color[0:3]}",
        lambda: f"{last_name}_{random_game[0:3]}",
        lambda: f"{random_city[0:3]}{birth_month_day}",
        lambda: f"{random_country[0:3]}_{first_name}"
    ]

    # Scegli una strategia in modo casuale e applicala
    return random.choice(strategies)()

def pad_string(string, length):
    return string.ljust(length, 'X')

def genera_consonanti(stringa):
    return ''.join([c for c in stringa.upper() if c not in 'AEIOU'])

def genera_vocali(stringa):
    return ''.join([c for c in stringa.upper() if c in 'AEIOU'])

def genera_codice_fiscale(last_name, first_name, gender, birth_date, birth_place):
    codice = ''

    # Estrai le consonanti e le vocali da cognome e nome
    consonanti_cognome = genera_consonanti(last_name)
    vocali_cognome = genera_vocali(last_name)
    consonanti_nome = genera_consonanti(first_name)
    vocali_nome = genera_vocali(first_name)

    # Costruisci il codice per il cognome
    codice_cognome = pad_string(consonanti_cognome + vocali_cognome, 3)
    codice += codice_cognome[:3]

    # Costruisci il codice per il nome
    codice_nome = pad_string(consonanti_nome + vocali_nome, 3)
    codice += codice_nome[:3]

    # Aggiungi la data di nascita e il genere
    giorno, mese, anno = birth_date.split('/')
    codice += anno[-2:]
    codice += 'ABCDEHLMPRST'[int(mese) - 1]
    if gender.upper() == 'F':
        giorno = str(int(giorno) + 40)
    codice += giorno.zfill(2)

    # Aggiungi un codice fittizio per il luogo di nascita
    codice += ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=4))

    return codice

# Funzione per generare dati casuali per un utente con email reale
def generate_random_user_data(fake):

    # Genera dati personali
    first_name = fake.first_name()
    last_name = fake.last_name()
    birth_date = fake.date_of_birth()
    gender = random.choice(["M", "F"])
    birth_place = fake.city()

    # Genera il codice fiscale
    cf = genera_codice_fiscale(last_name, first_name, gender, birth_date.strftime("%d/%m/%Y"), birth_place)

    # Genera l'username per l'account
    account_username = generate_username(first_name, last_name, birth_date, fake) + str(random.randint(10, 99))

    # Dizionario di provider di email fittizi
    fake_email_providers = [
    'gmail.com', 'libero.it', 'outlook.com', 'virgilio.it', 'hotmail.it', 'msn.com',
    'tiscali.it', 'alice.it', 'email.it', 'icloud.com', 'yahoo.it', 'sky.com',
    'poste.it', 'tim.it', 'me.com', 'aol.com', 'mail.com', 'proton.me', 
    'inbox.com', 'hotmail.com', 'live.it', 'yahoo.com', 'bol.com.br',
    'fastwebnet.it', 'tin.it', 'aruba.it', 'pec.it', 'teletu.it', 'mac.com',
    # Aggiungi altri provider comuni o specifici per l'Italia
]

    # Genera l'username per l'email
    email_username = generate_username(first_name, last_name, birth_date, fake) + str(random.randint(10, 99))
    email_provider = random.choice(fake_email_providers)
    email = f"{email_username}@{email_provider}"

    # Genera una password
    password = fake.password()

    return User(account_username, email, password, first_name, last_name, birth_date.strftime("%d/%m/%Y"), gender, birth_place, cf)

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
                attempts += 1
                if attempts >= max_attempts:
                    print(f"Massimo numero di tentativi raggiunto per l'utente {user.username}")
                    break
                sleep_time = 0.1 ** attempts
                # Rimuovere le print commentate per eseguire debug
                #print(f"Ritentare dopo {sleep_time} secondi")
                time.sleep(sleep_time)

    print(f"Utenti creati: {created}/{n}")

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
    
    # Rimuovere le print commentate per eseguire debug
    try:
        response.raise_for_status()
        #print(f"User {user_id} assigned to group {group_id} successfully")
    except HTTPError as e:
        #print(f"Failed to assign user {user_id} to group {group_id}. Error: {e.response.text}")
        return None

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
    for user in tqdm(users[:num_users_to_assign], desc="Assegnazione gruppi", unit="utente"):
        user_id = user['id']
        group_name, group_id = random.choice(list(group_ids.items()))
        assign_user_to_group(token, user_id, group_id)
        group_distribution[group_name] += 1

    # Stampa la distribuzione degli utenti nei gruppi
    for group_name, count in group_distribution.items():
        print(f"{group_name}: {count} utenti")

# Funzione per mostrare il menu e gestire le scelte dell'utente
def main_menu(fake):
    while True:
        clear_screen()  # Pulisce lo schermo all'inizio di ogni iterazione
        print("\nMenu:")
        print("3. Crea gruppi e assegna utenti")
        print("2. Crea n utenti casuali")
        print("1. Crea un singolo utente")
        print("0. Esci")
        print("\n")
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
            create_n_random_users(numero_utenti, fake)
        
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

        # Attendi un input dell'utente prima di pulire lo schermo
        input("\nPremi Invio per continuare...")

# Esecuzione del menu principale
if __name__ == "__main__":
    fake = Faker('it_IT')
    clear_screen()  # Pulisce lo schermo prima di mostrare il menu la prima volta
    main_menu(fake)