def create_docker_compose():
    keycloak_user = input("Inserisci l'username per l'amministratore Keycloak: ")
    keycloak_password = input("Inserisci la password per l'amministratore Keycloak: ")

    docker_compose_content = f"""version: '3'

volumes:
  postgres_data:
      driver: local

services:
  postgres:
      image: postgres
      volumes:
        - postgres_data:/var/lib/postgresql/data
      environment:
        POSTGRES_DB: keycloak
        POSTGRES_USER: keycloak
        POSTGRES_PASSWORD: password
  keycloak:
      image: quay.io/keycloak/keycloak:legacy
      environment:
        DB_VENDOR: POSTGRES
        DB_ADDR: postgres
        DB_DATABASE: keycloak
        DB_USER: keycloak
        DB_SCHEMA: public
        DB_PASSWORD: password
        KEYCLOAK_USER: {keycloak_user}
        KEYCLOAK_PASSWORD: {keycloak_password}
      ports:
        - 8080:8080
      depends_on:
        - postgres
"""

    with open('keycloack-postgres.yml', 'w') as file:
        file.write(docker_compose_content)

if __name__ == "__main__":
    create_docker_compose()
    print("File 'keycloack-postgres.yml' creato con successo.")
    

    