# Node
The main backend server.

## Running
*This guide assumes all systems are Linux-based. Official Aerial servers use CentOS 8.*

### Requirements
- A MySQL database
- A server to host the Discord bot
- Servers to host the Fortnite bots
- A self-signed certificate
- Linux command line experience

### Setting Up the Database
1. `CREATE USER 'aerial'@% IDENTIFIED BY 'password';`
2. `CREATE DATABASE "aerial";`
3. `CREATE TABLE "accounts" ("id" int NOT NULL AUTO_INCREMENT, "email" varchar(255) NOT NULL, "password" varchar(255) NOT NULL, "device_id" varchar(255) NOT NULL, "account_id" varchar(255) NOT NULL, "secret" varchar(255) NOT NULL, "in_use" tinyint(1) NOT NULL DEFAULT '0', PRIMARY KEY ("id"));`
4. ``GRANT ALL PRIVILEGES ON `aerial` TO 'aerial';``
5. `FLUSH PRIVILEGES;`

### Setting Up the Servers (Docker)
man idk im new to docker

### Setting Up the Servers (Standalone)
1. `useradd -r -s /bin/false aerial`
2. `mkdir /usr/local/lib/aerial`
3. Upload all files from repository into `/usr/local/lib/aerial`
4. Upload your certificate to `/usr/local/lib/aerial/ssl/cert.pem`
5. Upload your private key to `/usr/local/lib/aerial/ssl/key.pem`
6. Fill out `config.yml`
7. `pip3 install -r /usr/local/lib/aerial/requirements.txt`
8. `mv /usr/local/lib/aerial/aerial.service /etc/systemd/system/aerial.service`
9. `chown -R aerial:nobody /usr/local/lib/aerial`
10. `chmod -R 600 /usr/local/lib/aerial/`
11. `chmod 700 /usr/local/lib/aerial /usr/local/lib/aerial/ssl`
12. `systemctl daemon-reload`
13. `systemctl enable aerial`
