def create_docker_compose():
    keycloak_user = input("Inserisci l'username per l'amministratore Keycloak: ")
    keycloak_password = input("Inserisci la password per l'amministratore Keycloak: ")

    docker_compose_content = f"""version: '3.8'

services:
  keycloak:
    image: quay.io/keycloak/keycloak:latest
    environment:
      KEYCLOAK_USER: {keycloak_user}
      KEYCLOAK_PASSWORD: {keycloak_password}
      DB_VENDOR: POSTGRES
      DB_ADDR: postgres
      DB_DATABASE: keycloak
      DB_USER: keycloak
      DB_PASSWORD: password
    ports:
      - 8080:8080
    depends_on:
      - postgres

  postgres:
    image: postgres
    environment:
      POSTGRES_DB: keycloak
      POSTGRES_USER: keycloak
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
"""

    with open('docker-compose.yml', 'w') as file:
        file.write(docker_compose_content)

if __name__ == "__main__":
    create_docker_compose()
    print("File 'docker-compose.yml' creato con successo.")