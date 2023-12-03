import os
import requests
import json

# Configura l'URL del server Keycloak
KEYCLOAK_URL = "http://0.0.0.0:8080"  # Assicurati che questo indirizzo sia corretto
KEYCLOAK_REALM = "master"
KEYCLOAK_CLIENT_ID = "admin-cli"

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
            "grant_type": "password"
        }
        response = requests.post(url, data=data)
        response.raise_for_status()
        token = response.json()["access_token"]
        return token
    except requests.exceptions.RequestException as e:
        print(f"Errore durante l'ottenimento del token: {e}")
        return None

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
        print(f"Errore durante la creazione dell'utente: {e}")
        return None

# Funzione per mostrare il menu e gestire le scelte dell'utente
def main_menu():
    while True:
        print("\nMenu:")
        print("1. Crea un nuovo utente")
        print("0. Esci")
        scelta = input("Inserisci la tua scelta: ")

        if scelta == "1":
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
