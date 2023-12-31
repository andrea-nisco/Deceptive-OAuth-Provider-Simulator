FROM alpine:latest

# Installa OpenJDK 17, wget, file, PostgreSQL, Python e pulisce la cache
RUN apk add --no-cache openjdk17 wget file postgresql postgresql-client python3 py3-pip curl openssl

# Crea un ambiente virtuale Python e installa i pacchetti necessari
RUN python3 -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip3 install faker requests tqdm PyJWT

# Scarica e installa Keycloak
RUN wget https://github.com/keycloak/keycloak/releases/download/23.0.1/keycloak-23.0.1.tar.gz -O /tmp/keycloak.tar.gz && \
    ls -l /tmp/keycloak.tar.gz && \
    file /tmp/keycloak.tar.gz && \
    tar -xzf /tmp/keycloak.tar.gz -C /opt && \
    rm /tmp/keycloak.tar.gz

# Configura PostgreSQL
RUN mkdir -p /run/postgresql && chown -R postgres:postgres /run/postgresql && \
    mkdir -p /var/lib/postgresql/data && chown -R postgres:postgres /var/lib/postgresql/data

# Copia i file necessari nell'immagine
COPY ./app/*.py /app/

# Assegna i permessi di esecuzione allo script entrypoint.sh
COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh

# Espone la porta 8080 per Keycloak
EXPOSE 8080

# Imposta la directory di lavoro (opzionale)
WORKDIR /app

# Imposta lo script entrypoint.sh come punto di ingresso
ENTRYPOINT ["/entrypoint.sh"]
