# docker run -it -p 8080:8080 -v pgdata:/var/lib/postgresql/data -v keycloakdata:/opt/keycloak-23.0.1/standalone/data test

from faker import Faker
from tqdm import tqdm
import os
import random
import time

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

def delete_random_users(fake):
    token = get_token()
    if not token:
        print("Impossibile ottenere il token di accesso.")
        return

    all_users = get_all_users(token)
    if not all_users:
        print("Nessun utente trovato.")
        return

    num_users_to_delete = int(input("Inserisci il numero di utenti da cancellare: "))
    if num_users_to_delete > len(all_users):
        print(f"Errore: il numero di utenti da cancellare ({num_users_to_delete}) è maggiore del totale degli utenti ({len(all_users)}).")
        return

    with tqdm(total=num_users_to_delete, desc="Cancellazione utenti", unit="utente") as pbar:
        for _ in range(num_users_to_delete):
            user_to_delete = random.choice(all_users)
            delete_user(token, user_to_delete['id'])
            all_users.remove(user_to_delete)
            pbar.update(1)  # Aggiorna la barra di progressione

    print(f"Totale utenti cancellati: {num_users_to_delete}")

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
        print("5. Verifica il numero utenti presenti nel database")
        print("4. Cancella n utenti casuali")
        print("3. Crea gruppi e assegna utenti")
        print("2. Crea n utenti casuali")
        print("1. Crea un singolo utente")
        print("0. Esci")
        print("\n")
        scelta = input("Inserisci la tua scelta: ")

        if scelta == "5":
            token = get_token()
            if token:
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