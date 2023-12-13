# docker run -it -p 8080:8080 -v pgdata:/var/lib/postgresql/data -v keycloakdata:/opt/keycloak-23.0.1/standalone/data -v keycloak_creds:/opt/keycloak-23.0.1/credentials test -v

from faker import Faker
from tqdm import tqdm
import os
import random

from config import *
from user import *
from keycloak_utils import *

def clear_screen():
    # Windows
    if os.name == 'nt':
        _ = os.system('cls')
    # MacOS/Linux
    else:
        _ = os.system('clear')

def add_user_to_database(token):
    user = input_user_data()
    return create_user(token, user)

def delete_random_users(fake):
    token = get_token()
    if not token:
        print("Impossibile ottenere il token di accesso.")
        return

    print("Recupero del numero di utenti in corso...")
    all_users = get_all_users(token)
    total_users = len(all_users)
    print(f"Numero totale di utenti nel database: {total_users}")
    
    if not all_users:
        print("Nessun utente trovato.")
        return

    num_users_to_delete = int(input("Inserisci il numero di utenti da cancellare: "))
    if num_users_to_delete > len(all_users):
        print(f"Errore: il numero di utenti da cancellare ({num_users_to_delete}) è maggiore del totale degli utenti ({len(all_users)}).")
        return

    with tqdm(total=num_users_to_delete, desc="Cancellazione utenti", unit="utente") as pbar:
        for _ in range(num_users_to_delete):
            if token_scaduto(token):
                token = get_token()
                if not token:
                    print("Impossibile rinnovare il token di accesso.")
                    break

            user_to_delete = random.choice(all_users)
            delete_user(token, user_to_delete['id'])
            all_users.remove(user_to_delete)
            pbar.update(1)  # Aggiorna la barra di progressione

    print(f"Totale utenti cancellati: {num_users_to_delete}")

def create_oauth_client_menu():
    print("\nCreazione di un nuovo client OAuth in Keycloak.")

    token = get_token()  # Assicurati che questa funzione restituisca un token valido
    if not token:
        print("Impossibile ottenere il token di accesso.")
        return

    # Raccogli i dati necessari dall'utente
    client_name = input("Inserisci il nome del client: ")
    redirect_uri = input("Inserisci l'URI di reindirizzamento del client: ")
    client_root_url = input("Inserisci l'URL di base del client: ")
    client_type = input("Inserisci il tipo di client (public/confidential): ").lower()

    is_public = client_type == 'public'

    # Crea un dizionario con i dati del client
    client_data = {
        'clientId': client_name,
        'enabled': True,
        'publicClient': is_public,
        'redirectUris': [redirect_uri],
        'webOrigins': [client_root_url],
        'protocol': 'openid-connect',
        'standardFlowEnabled': True,  # Per il flusso di autorizzazione standard
        'implicitFlowEnabled': False,  # Impostare su True se necessario
        'directAccessGrantsEnabled': True,  # Per l'autenticazione diretta
        'serviceAccountsEnabled': False,  # Impostare su True se il client ha bisogno di un account di servizio
        'attributes': {
            'pkce.code.challenge.method': 'S256',
            'oauth2.device.authorization.grant.enabled': 'true'
        },
    }

    # Chiama la funzione per creare il client
    try:
        client_id = create_oauth_client(token, client_data)
        if client_id:
            print(f"Client OAuth creato con successo. ID Client: {client_id}")
        else:
            print("Errore nella creazione del client OAuth. Nessuna risposta dal server.")
    except Exception as e:
        print(f"Errore nella creazione del client OAuth: {str(e)}")

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
        print("9. Assegna un gruppo ad un ruolo")
        print("8. Crea un ruolo")
        print("7. Crea n utenti casuali con gruppo")
        print("6. Crea un nuovo client OAuth in Keycloak")
        print("5. Verifica il numero utenti presenti nel database")
        print("4. Cancella n utenti casuali")
        print("3. Crea gruppi e assegna utenti")
        print("2. Crea n utenti casuali")
        print("1. Crea un singolo utente")
        print("0. Esci")
        print("\n")
        scelta = input("Inserisci la tua scelta: ")

        if scelta == "9":
            group_name = input("Inserisci nome gruppo che vuoi aggiungere: ")
            role_name = input("Inserisci nome ruolo che vuoi assegnare al gruppo: ")

            group_id = get_group_id(group_name)
            if group_id:
                assign_group_to_role(group_id, role_name)

        elif scelta == "8":
            create_role()
        
        elif scelta == "7":
            create_n_random_users_and_assign_to_group(fake)

        elif scelta == "6":
            create_oauth_client_menu()

        elif scelta == "5":
            token = get_token()
            if token:
                print("Recupero del numero di utenti in corso...")
                all_users = get_all_users(token)
                total_users = len(all_users)
                print(f"Numero totale di utenti nel database: {total_users}")
            else:
                print("Impossibile ottenere il token di accesso.")

        elif scelta == "4":
            delete_random_users(fake)

        elif scelta == "3":
            token = get_token()
            if token:
                all_users = get_all_users(token)
                if all_users:
                    total_users = len(all_users)
                    print(f"Numero totale di utenti nel database: {total_users}")
                    num_users_to_assign = 0
                    while True:
                        try:
                            num_users_to_assign = int(input("Quanti utenti vuoi distribuire nei gruppi?: "))
                            if num_users_to_assign > total_users:
                                print(f"Errore: hai inserito un numero maggiore del totale di utenti disponibili ({total_users}).")
                                continue
                            break
                        except ValueError:
                            print("Errore: inserisci un numero intero.")

                    num_gruppi = 0
                    while True:
                        try:
                            num_gruppi = int(input("Inserisci il numero di gruppi da creare: "))
                            break
                        except ValueError:
                            print("Errore: inserisci un numero intero.")

                    group_names = [input(f"Inserisci il nome per il gruppo {i+1}: ") for i in range(num_gruppi)]
                    create_groups_and_assign_users(group_names, num_users_to_assign)
            else:
                print("Impossibile ottenere il token di accesso.")

        elif scelta == "2":
            numero_utenti = int(input("Con quanti utenti vuoi popolare il database?: "))
            create_n_random_users(numero_utenti, fake)
        
        elif scelta == "1":
            token = get_token()
            add_user_to_database(token)

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