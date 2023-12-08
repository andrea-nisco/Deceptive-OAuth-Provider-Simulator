import random  
import getpass
import datetime

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
            birth_date = datetime.datetime.strptime(birth_date_input, "%d/%m/%Y").strftime("%d/%m/%Y")
            break
        except ValueError:
            print("Formato data non valido. Riprova.")

    gender = input("Inserisci genere: ")
    birth_place = input("Inserisci luogo di nascita: ")
    cf = input("Inserisci codice fiscale: ")

    return User(username, email, password, first_name, last_name, birth_date, gender, birth_place, cf)

def generate_username(first_name, last_name, birth_date, fake):
    elements = {
        'first_name': first_name,
        'last_name': last_name,
        'birth_year': birth_date.strftime("%Y"),
        'birth_month_day': birth_date.strftime("%m%d"),
        'random_word': fake.word().lower(),
        'random_game': fake.word().lower(),
        'random_color': fake.color_name().lower().replace(" ", ""),
        'random_city': fake.city().lower().replace(" ", ""),
        'random_country': fake.country().lower().replace(" ", "")
    }

    # Numero di elementi da includere (es. tra 2 e 4)
    num_elements = random.randint(2, 4)

    # Scegliere casualmente gli elementi e l'ordine
    chosen_elements = random.sample(elements.keys(), num_elements)
    username_parts = [elements[element] for element in chosen_elements]

    # Opzionale: aggiungere separatori o numeri casuali
    separator = random.choice(['.', '_', ''])
    if random.choice([True, False]):
        username_parts.append(str(random.randint(0, 99)))

    return separator.join(username_parts)

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
