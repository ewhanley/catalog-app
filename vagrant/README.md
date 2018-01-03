# Project 4: Item Catalog

This project is a Flask-based CRUD web application that provides a catalog of used cars for sale by type (SUV, Coupe, etc). The project incorporates responsive design to ensure consistent UX from any viewport. It includes an OAuth2-based user registration system whereby users can log in with either Google or Facebook. Once registered, users have the ability to create, edit, and delete their own posts as well as read posts created by other users.

![Screenshot of Item Catalog main page](screenshots/main.png)

## Motivation

This project is the fourth in a series of projects I am completing for Udacity's [Full Stack Web Developer Nanodegree](https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd004).

## Getting Started

These instructions will explain how to get a copy of this project running on your local machine.

### Prerequisites

* Python 2.x
* VirtualBox
* Vagrant
* An App ID from Facebook
* An OAuth 2.0 client ID from Google

### How to Run Project

1. Install VirtualBox. You can download it from virtualbox.org [here](https://www.virtualbox.org/wiki/Downloads), or if you use [Homebrew](https://brew.sh/) you can type the following in your terminal:

    ```bash

    > brew cask install virtualbox
    ```

2. Install Vagrant. You can download it from vagrantup.com [here](https://www.vagrantup.com/downloads.html), or if you use [Homebrew](https://brew.sh/) you can type the following in your terminal:

    ```bash

    > brew cask install vagrant
    ```

3. Download or clone this repository to your machine. Navigate to the project directory:

    ```bash

    > git clone https://github.com/ewhanley/udacity-full-stack.git
    > cd udacity-full-stack/backend-project/vagrant
    ```

4. Get a Facebook App ID by creating a new web-app:
   - Go [here](https://developers.facebook.com/quickstarts/?platform=web) to register a new web app. Start by naming the app whatever you'd like. I called mine *Udacity Backend Project*.
   - Choose *Skip Quick Start* in the upper right.
   - Select *Settings* from the left panel, scroll to the bottom, and enter *http://localhost:5000/* for the *Site URL*.
   - Now, in the left panel, choose *+ Add Product* and add *Facebook Login*
   - Under Facebook Login settings, add *http://localhost:5000/* to *Valid OAuth redirect URIs*
   - Finally, paste your App ID and App Secret into a json file and save it in the project root (`/vagrant`) directory as `fb_client_secrets.json`. The file should have the following format:
        ```json

        {
            "web": {
                "app_id": "PASTE_YOUR_APP_ID_HERE",
                "app_secret": "PASTE_YOUR_APP_SECRET_HERE"
            }
        }
        ```

5. Get a Google OAuth 2.0 client ID and client secret
   - Go [here](https://console.developers.google.com/apis/dashboard) and create a new project via the dropdown in the upper left of the page.
   - Once the project is completed, select *OAuth client ID* from the *Create credentials* dropdown in the middle of the page.
   - Follow the prompts, selecting *Web application* as the Application type. Also, add *http://localhost:5000/* as an Authorized Javascript origin and add *http://localhost:5000* and *http://localhost:5000/login* and *http://localhost:5000/gconnect* to the list of Authorized redirect URIs.
   - Once the credentials are created, download the corresponding JSON file and save it as `g_client_secrets.json` in the project root directory (`\vagrant`).
   - Lastly replace the client ID on line 40 of `templates\login.html` with your client ID:

        ```html

        <span class="g-signin" data-scope="openid email" data-clientid="YOUR_GOOGLE_CLIENT_ID_HERE"
        ```

6. Navigate to the `udacity-full-stack/backend-project/vagrant` and start the virtual machine by typing:

    ```bash

    > vagrant up

This step will take several minutes the first time you run it as it will install all of the required library dependencies for Python as well as populate the database with some example users and cars. If you're interested in the details[<sup>1</sup>](#notes) of this, check out `vagrant/Vagrantfile`, which is a slightly modified version of the config provided by Udacity as part of this project.

6. After the VM is up and running, log into it by typing:

    ```bash

    > vagrant ssh

7. Once you are logged into the VM, you will have a new prompt in your terminal. Navigate to the project directory:

    ```bash

    vagrant@vagrant:~$ cd /vagrant
    ```

8. Finally, run the Python script:

    ```bash

    vagrant@vagrant:/vagrant$ python project.py
    ```

[####Notes](#notes)
1. The VM is configured such that all Python dependencies are pre-installed. Additionally, the database pre-populated the first time the VM is provisioned. If you ever want to refresh the database to its initial state, you can run `remove_db.sh`. Then you can type `exit` or `Ctrl-d` to get back to your machine's prompt where you can run the following, which will reload the VM and re-populate the database:

    ```bash

    > vagrant reload --provision
    ```

2. All images were sourced from [Pixabay](https://pixabay.com/) and are used under the Creative Commons CC0 license.
3. All OAuth2 work is based on the OAuth module presented in the *The Backend: Databases & Applications* module of the Full Stack Nanodegree
