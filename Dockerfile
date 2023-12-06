FROM alpine:latest

# Installa OpenJDK 17, wget, file, PostgreSQL, e Python
RUN apk add --no-cache openjdk17 wget file postgresql postgresql-client python3 py3-pip

# Installa le librerie necessarie
RUN pip3 install faker requests tqdm PyJWT

# Scarica Keycloak versione 23.0.1
RUN wget https://github.com/keycloak/keycloak/releases/download/23.0.1/keycloak-23.0.1.tar.gz -O /tmp/keycloak.tar.gz

# Verifica il file scaricato e estrai Keycloak
RUN ls -l /tmp/keycloak.tar.gz \
    && file /tmp/keycloak.tar.gz \
    && tar -xzf /tmp/keycloak.tar.gz -C /opt \
    && rm /tmp/keycloak.tar.gz

# Crea la directory necessaria per PostgreSQL
RUN mkdir -p /run/postgresql && chown -R postgres:postgres /run/postgresql
RUN mkdir -p /var/lib/postgresql/data && chown -R postgres:postgres /var/lib/postgresql/data

# Copia lo script entrypoint.sh nell'immagine
COPY entrypoint.sh /entrypoint.sh

# Copia lo script Python per popolare il database
COPY main.py /main.py
COPY keycloak_utils.py /keycloak_utils.py
COPY user.py /user.py
COPY config.py /config.py

RUN chmod +x /entrypoint.sh

# Espone la porta 8080 per Keycloak
EXPOSE 8080

# Imposta lo script entrypoint.sh come punto di ingresso
ENTRYPOINT ["/entrypoint.sh"]
