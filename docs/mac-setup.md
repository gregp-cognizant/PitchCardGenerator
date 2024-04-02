# Docker Desktop Setup for Mac

## Prerequisites

- Ensure you have administrative privileges on your Mac. If not, [request temporary admin access here](https://ctsccprod.service-now.com/ss?id=sc_cat_item&sys_id=c1e096091b9a8d54761621fcbc4bcb98)
  - Fill out your project name
  - Fill out the rest of the details as best you can
  - If *Select Software Entitlement* list is empty, then you will need to click the checkbox *If required Version (or) Software Entitlement...*
    - Fill out the new boxes as best you can or put N/A if not applicable
    - For Software url: *https://www.docker.com/products/docker-desktop/*
    - For Business Justification put: "Gen AI training course"

## Installation Steps

### Step 1: Verify Your Mac's Chip
- Click on the Apple logo at the upper left corner of your screen.
- Select "About This Mac".
- Note the chip type, Intel or Apple Silicon(m1/m2).

![Verify Chip](https://github.com/Tech-Modernization/AgentFramework/assets/149821365/99e93717-8615-474a-a4f3-0c2d25fceef9)

### Step 2: Download Docker Desktop
- Visit the [Docker Desktop download page](https://docs.docker.com/desktop/install/mac-install/).
- Choose the version of Docker Desktop corresponding to your Mac's chip.

![Download Docker](https://github.com/Tech-Modernization/AgentFramework/assets/149821365/51ee4adc-96d8-4873-94ae-fa134ec08250)

### Step 3: Install Docker Desktop
There are two approaches to install Docker Desktop

#### Option 1: Using Terminal
Execute the following commands in the Terminal:
```bash
sudo hdiutil attach Docker.dmg
sudo /Volumes/Docker/Docker.app/Contents/MacOS/install
sudo hdiutil detach /Volumes/Docker
```

#### Option 2: Using the installer

- After downloading Docker Desktop, locate the downloaded `.dmg` file.
- Double-click on the DMG file to open the installer.
- Follow the on-screen instructions to complete the installation.


For detailed installation instructions, visit the [Docker Desktop installation guide](https://docs.docker.com/desktop/install/mac-install/).

# Verifying Docker Desktop Installation

### Step 4: Check Docker Desktop Version

To ensure that Docker Desktop is installed correctly on your Mac, follow these steps:

- Open the Terminal.
- Execute the following command:
  ```bash
  docker --version

![Installer Method](https://github.com/Tech-Modernization/AgentFramework/assets/149821365/de47f080-646b-474e-bda6-ba70220bb42d)

### Step 5: Start Docker Desktop
- Navigate to your Applications folder in Finder
- Locate Docker.app
- Double click on Docker.app to open it
- Once Docker Desktop starts, you will see a Docker icon in the top menu bar
