# Docker Desktop Setup for Windows

## Prerequisites

- Ensure you have administrative privileges on your PC. If not, [submit Request Software Asset for install of Docker Desktop ](https://ctsccprod.service-now.com/ss?id=sc_cat_item&sys_id=c1e096091b9a8d54761621fcbc4bcb98)
  - Fill out your project name
  - Fill out the rest of the details as best you can
  - If *Select Software Entitlement* list is empty, then you will need to click the checkbox *If required Version (or) Software Entitlement...*
    - Fill out the new boxes as best you can or put N/A if not applicable
    - For Software url: *https://www.docker.com/products/docker-desktop/*
    - For Business Justification put: "Gen AI training course"

## Step 1: Download Docker Desktop
- Visit the [Docker Desktop for Windows download page](https://docs.docker.com/desktop/windows/install/).
- Download the Docker Desktop Installer.

![Download Docker](https://github.com/Tech-Modernization/AgentFramework/assets/149821365/23fbf449-4fc0-4844-b18e-a2f470f8e5a9)

## Step 2: Run the Installer
- Locate the downloaded `Docker Desktop Installer.exe` file.
- Double-click on the file to initiate the installation process.

## Step 3: Configure Installation Options
- During the installation, you will be prompted to choose your preferred backend (WSL 2 or Hyper-V).
- Select the option that is compatible with your system or your preference.

## Step 4: Complete Installation
- Follow the instructions provided by the installation wizard.
- Authorize the installer as required.
- Once the installation is successful, click `Close` to finish.

## Step 5: Configure Docker Users Group (If Necessary)
- If your administrative account differs from your user account, you need to add your user account to the `docker-users` group.
- Run `Computer Management` as an administrator.
- Navigate to `Local Users and Groups > Groups > docker-users`.
- Right-click and add your user account to the group.
- Sign out and then sign back in for the changes to take effect.

## Additional Steps for WSL Integration

- Ensure you have the Windows Subsystem for Linux (WSL) installed.
- From the WSL Command Line Interface (CLI), clone the desired repository into the WSL file system.

For more detailed instructions and troubleshooting, refer to the [official Docker documentation for Windows](https://docs.docker.com/desktop/windows/troubleshoot/).
