# DjangoRide
Ubuntu20.04

sudo apt-get update
sudo apt-get upgrade

Install python3.8.10, pip, virtual env
sudo apt install python3
sudo apt install python3-pip
sudo apt install python3-venv
sudo apt-get install libpq-dev python-dev libxml2-dev libxslt1-dev libldap2-dev libsasl2-dev libffi-dev libjpeg-dev zlib1g-dev


Install postgres12.15
sudo apt-get update
sudo apt -y install postgresql-12 postgresql-client-12
To check the status
systemctl status postgresql.service


Django and virtual env installation
cd /opt/
mkdir Django
cd Django/

Clone the project
sudo git clone https://github.com/jithinkr12345/DjangoRide.git
Virtual setup
python3 -m venv venvDjango
Activate the virtual python
source venvDjango/bin/activate

cd DjangoRide/
pip install -r requirements.txt 
python -m pip install requests

Create database in postgres
su - postgres
psql
CREATE DATABASE ride_db;
\password
Give as root
\q
exit
Restart postgres
sudo systemctl restart postgresql

python3 manage.py makemigrations
python3 manage.py migrate