# Project 4: Item Catalog

This project is a CRUD web application that provides a catalog of used cars for sale by type (SUV, Coupe, etc). It provides an OAuth2-based user registration system whereby users can log in with either Google or Facebook. Once registered, users have the ability to create, edit, and delete their own posts.

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

4. Get a Facebook App ID by creating a new web-app
   - Go [here](https://developers.facebook.com/quickstarts/?platform=web) to register a new web app. Start by naming the app whatever you'd like. I called mine *Udacity Backend Project*.
   - Choose *Skip Quick Start* in the upper right.
   - Select *Settings* from the left panel, scroll to the bottom, and enter *http://localhost:5000/* for the *Site URL*.
   - Now, in the left panel, choose *+ Add Product* and add *Facebook Login*
   - Under Facebook Login settings, add *http://localhost:5000/* to *Valid OAuth redirect URIs*
   - Finally, paste your App ID and App Secret into a json file and save it in the project root directory as `fb_client_secrets.json`.  
5. Copy
4. Download the data to populate the project database [here](https://d17h27t6h515a5.cloudfront.net/topher/2016/August/57b5f748_newsdata/newsdata.zip). **You will have to extract the file and put the `newsdata.sql` file into the `/vagrant` directory from Step 3.**

5. Next, start the virtual machine by typing:

    ```bash

    > vagrant up

This step will take several minutes the first time you run it as it will install all of the required library dependencies for Python as well as hydrate the database. If you're interested in the details of this, check out `vagrant/Vagrantfile`, which is a slightly modified version of the config provided by Udacity as part of this project.

6. After the VM is up and running, log into it by typing:

    ```bash

    > vagrant ssh

7. Once you are logged into the VM, you will have a new prompt in your terminal. Navigate to the project directory:

    ```bash

    vagrant@vagrant:~$ cd /vagrant
    ```

8. Finally, run the Python script:

    ```bash

    vagrant@vagrant:/vagrant$ python3 logs_analysis.py
    ```

    or

    ```bash

    vagrant@vagrant:/vagrant$ ./logs_analysis.py
    ```

The script will output three questions and their answers in tabular format to the terminal. It will also write the same text to a file called `output.txt` in the `vagrant' directory. The following is a snippet of the question and tabulated answer output:

    Who are the most popular article authors of all time?
    | Author                 |   Views |
    |------------------------+---------|
    | Ursula La Multa        |  507594 |
    | Rudolf von Treppenwitz |  423457 |

**Note:** The VM is configured such that all Python dependencies are pre-installed. Additionally, the database is rebuilt each time the VM image is reloaded. If you ever need to refresh the database, you can type `exit` or `Ctrl-d` to get back to your machine's prompt where you can run:

```bash

> vagrant reload --provision
```

This will reload the VM from the config in Vagrantfile, which will recreate the database.