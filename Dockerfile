# Utilizza l'immagine di base ufficiale di Keycloak
FROM quay.io/keycloak/keycloak:latest

# Imposta la variabile di ambiente per l'accesso automatico all'admin
ENV KEYCLOAK_USER=admin
ENV KEYCLOAK_PASSWORD=admin

# Imposta l'hostname di Keycloak e la modalità di sviluppo
ENV KC_HOSTNAME=localhost
ENV KC_HTTP_ENABLED=true

# Copia il file del realm (ad esempio my-realm.json) nel container
COPY ./my-realm.json /tmp/my-realm.json

# Espone la porta su cui Keycloak ascolta
EXPOSE 8080

# Imposta il punto di ingresso e il comando di default
ENTRYPOINT ["/opt/keycloak/bin/kc.sh"]

# Importa il realm al momento dell'avvio del server e avvia in modalità sviluppo
CMD ["start-dev", "--import-realm"]

