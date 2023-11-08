from faker import Faker
import json

fake = Faker()

def generate_fake_users(num_users):
    users = []
    for _ in range(num_users):
        first_name = fake.first_name()
        last_name = fake.last_name()
        user = {
            "username": fake.user_name(),
            "enabled": True,
            "emailVerified": True,
            "firstName": first_name,
            "lastName": last_name,
            "email": fake.email(),
            "credentials": [
                {
                    "type": "password",
                    "value": fake.password(),
                    "temporary": False
                }
            ],
            "realmRoles": ["user"],
            "clientRoles": {
                "account": ["view-profile", "manage-account"]
            }
        }
        users.append(user)
    return users

def add_users_to_realm(realm_file_path, num_users):
    with open(realm_file_path, 'r+') as file:
        realm_data = json.load(file)
        fake_users = generate_fake_users(num_users)
        if "users" in realm_data:
            realm_data["users"].extend(fake_users)
        else:
            realm_data["users"] = fake_users
        file.seek(0)  # Rewind file to the beginning.
        json.dump(realm_data, file, indent=2)

# Replace 'my-realm.json' with the path to your Keycloak realm file
# and '5' with the number of fake users you want to generate.
add_users_to_realm('my-realm.json', 5)

