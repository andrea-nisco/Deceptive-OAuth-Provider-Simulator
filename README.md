# Deceptive-OAuth-Provider-Simulator

Welcome to the "Deceptive OAuth Provider Simulator" - a cutting-edge cybersecurity project designed to protect real assets by luring attackers to a simulated OAuth2.0 provider. This decoy, developed as part of a master's program, serves as a digital honeypot, strategically deceiving potential adversaries.

## Getting Started

To get this project up and running, you'll need to follow a few simple steps. Don't worry, we'll guide you through each one!

### Prerequisites

Make sure you have Docker installed on your machine. If you're using Windows, you'll need to execute a few additional commands to set things up:

1. **Start Docker**

   Just the usual routine to get Docker running on your machine.

2. **Windows Configuration**

   Run these commands in your PowerShell to set up the necessary environment:

   - Execute Policy Change:
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
     (Make sure to run this in the repo folder)

### Installation

Now, let's build and run the simulator.

1. **Build the Docker Image**

   Execute the following command to build the Docker image:
