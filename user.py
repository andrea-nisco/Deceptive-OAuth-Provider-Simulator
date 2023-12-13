import random  
import getpass
import datetime
from datetime import datetime, timedelta

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

def input_user_data():
    username = input("Inserisci username: ")
    email = input("Inserisci email: ")
    password = getpass.getpass("Inserisci password: ")
    first_name = input("Inserisci nome: ")
    last_name = input("Inserisci cognome: ")
    
    # Gestione dell'input della data con il formato corretto
    while True:
        birth_date_input = input("Inserisci data di nascita (gg/mm/aaaa): ")
        try:
            birth_date = datetime.strptime(birth_date_input, "%d/%m/%Y").strftime("%d/%m/%Y")
            break
        except ValueError:
            print("Formato data non valido. Riprova.")

    gender = input("Inserisci genere (M/F): ")
    birth_place = input("Inserisci luogo di nascita: ")
    cf = input("Inserisci codice fiscale: ")

    return User(username, email, password, first_name, last_name, birth_date, gender, birth_place, cf)

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
    if len(consonanti_nome) >= 4:
        codice_nome = consonanti_nome[0] + consonanti_nome[2] + consonanti_nome[3]
    else:
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
    alfabeto_esteso = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ' + birth_place.upper())
    codice += ''.join(random.choices(list(alfabeto_esteso), k=4))

    return codice

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

    #Genera una carta di credito casuale
def generate_card_info_v2():
    # Generate a random 16 digit card number
    card_number = ''.join([str(random.randint(0, 9)) for _ in range(16)])

    # Generate a random expiration date within the next 20 years
    today = datetime.today()
    max_future_years = 20
    future_date = today + timedelta(days=365 * max_future_years)
    expiration_year = random.randint(today.year, future_date.year)
    expiration_month = random.randint(1, 12)
    expiration_day = random.randint(1, 28)  # To avoid complications with February

    # Format the expiration date as DD/MM/YYYY
    expiration_date = f"{str(expiration_day).zfill(2)}/{str(expiration_month).zfill(2)}/{expiration_year}"

    # Generate a random 3 digit CVV
    cvv = ''.join([str(random.randint(0, 9)) for _ in range(3)])

    return card_number, expiration_date, cvv