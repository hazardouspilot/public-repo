Instructions for running app on AWS

Create EC2 instance:
 - IAM instance profile: select LabInstanceProfile

Link via SSH (PuTTY) to EC2:
 - private key = .ppk file, hostname = ubuntu@[your_instance_public_DNS], connection 300s

Install stuff on EC2 instance (putty):
mkdir <projdir>
cd <projdir>
sudo apt update
sudo apt install python3-pip
pip install pipenv
sudo apt install pipenv
sudo apt install nginx
sudo apt install gunicorn
systemctl status nginx -> :q to quit
sudo nano /etc/nginx/sites-enabled/default
location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
ctrl + O to save
enter
ctrl + X to exit
pipenv install
pipenv shell
pipenv install flask
pipenv install boto3
pipenv install werkzeug
pipenv install jinja2
pipenv install gunicorn
pipenv install requests

Filezilla:
File-site manager-new site
SFTP
host=[your_instance_public_DNS]
port=22
login type:key file
browse:.ppk
user=ubuntu
connect

place app.py and template folder into /home/ubuntu/<projdir>

Modify configuration (Putty)
sudo cp /etc/nginx/sites-available/default /etc/nginx/sites-available/<projdir>
sudo nano /etc/nginx/sites-available/<projdir>
server {
    listen 80;
    server_name <instance_public_DNS>;
    index index.html index.htm index.nginx-debian.html home.html mainpage.html register.html;
    location / {
        proxy_pass http://127.0.0.1:8000;  # Change port if Gunicorn is running on a different port
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
ctrl + O to save
enter
ctrl + X to exit
sudo ln -s /etc/nginx/sites-available/musicApp /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-available/default
sudo chmod -R 777 /etc/nginx/sites-enabled
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
gunicorn "app:app" -b 0.0.0.0 --daemon


If EC2 already running with installations and configurations:

reconnect to ec2 using putty
cd to <projdir> folder
pipenv shell
sudo nano /etc/nginx/sites-available/<projdir>
update the server (DNS address)
sudo systemctl reload nginx
gunicorn "app:app" -b 0.0.0.0 --daemon