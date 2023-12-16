# Deceptive-OAuth-Generator-Component

Welcome to the "Deceptive OAuth Generator Component." This project is an advanced cybersecurity initiative developed to safeguard real-world assets by redirecting potential attackers to a fabricated OAuth2.0 provider. Created as a key component of a master's program, this tool functions as an effective digital honeypot, strategically misleading adversaries.

## Getting Started

This section outlines the necessary steps to set up and run the Deceptive OAuth Provider Simulator. The instructions are straightforward and designed to facilitate a smooth setup process.

### Prerequisites

Ensure Docker is installed on your system. Users operating on Windows must perform additional steps for proper configuration:

1. **Initiate Docker**

   Standard procedure to activate Docker on your system.

2. **Windows Configuration**

   Execute the following commands in PowerShell to prepare your environment:

   - Policy Adjustment:
     ```
     Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
     ```

   - Install dos2unix:
     ```
     choco install dos2unix
     ```

   - Convert 'entrypoint.sh':
     ```
     dos2unix entrypoint.sh
     ```
     Note: Run this command within the repository directory.

### Installation

Follow these steps to build and deploy the simulator.

1. **Docker Image Construction**

   Use this command to construct the Docker image:
   ```
   docker build -t test .
   ```
3. **Launching the Docker Container**

   To initiate the simulator, execute:
   ```
   docker run -it -p 8080:8080 -v pgdata:/var/lib/postgresql/data -v keycloakdata:/opt/keycloak-23.0.1/standalone/data -v keycloak_creds:/opt/keycloak-23.0.1/credentials test -v
   ```
## Conclusion

The Deceptive OAuth Provider Simulator is now fully operational. It stands ready to serve as an advanced tool in your cybersecurity arsenal.

For any technical issues or inquiries, please contact our support team. We appreciate your commitment to enhancing digital security.
