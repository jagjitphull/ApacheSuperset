cat apache-superset-install.sh 
#!/bin/bash

# Exit on any error
set -e

# Update and install necessary system dependencies
sudo dnf update -y
sudo dnf install -y gcc gcc-c++ libffi-devel python3-devel git libpq-devel postgresql postgresql-server redis python3-pip nginx openssl

# Initialize PostgreSQL and configure data directory
echo "Initializing PostgreSQL and setting up the data directory..."

# Ensure PostgreSQL service is disabled before initialization
sudo systemctl disable postgresql --now

# Set PostgreSQL data directory (change this if you need a custom directory)
PGSQL_DATA_DIR="/var/lib/pgsql/data"

# Initialize PostgreSQL
sudo postgresql-setup --initdb

# Ensure correct ownership and permissions of the data directory
sudo chown -R postgres:postgres $PGSQL_DATA_DIR
sudo chmod 700 $PGSQL_DATA_DIR


# Modify pg_hba.conf to use password-based authentication (md5)
PG_HBA_CONF="/var/lib/pgsql/data/pg_hba.conf"
echo "Updating PostgreSQL authentication method to 'md5' in pg_hba.conf..."
sudo sed -i "s/^host\s*all\s*all\s*127.0.0.1\/32\s*ident/host    all   all   127.0.0.1\/32   md5/" $PG_HBA_CONF
sudo sed -i "s/^host\s*all\s*all\s*::1\/128\s*ident/host    all  all         ::1\/128   md5/" $PG_HBA_CONF

# Enable and start PostgreSQL
sudo systemctl enable --now postgresql
sudo systemctl start postgresql

# Switch to PostgreSQL user and create the Superset database and user
echo "Setting up PostgreSQL database and user for Superset..."
sudo -u postgres psql <<EOF
CREATE DATABASE superset_prod_db;
CREATE USER superset_prod_user WITH PASSWORD 'superset_password';
ALTER ROLE superset_prod_user SET client_encoding TO 'utf8';
ALTER ROLE superset_prod_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE superset_prod_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE superset_prod_db TO superset_prod_user;
EOF


# Create Superset directory and set up Python virtual environment
pip3 install virtualenv 
mkdir ~/superset
cd ~/superset
touch ~/superset/superset_config.py
python3 -m venv venv
source venv/bin/activate


# Upgrade pip and install Apache Superset globally
echo "Installing Apache Superset and dependencies..."
sudo pip3 install --upgrade pip
sudo pip3 install apache-superset psycopg2-binary redis celery pillow

# Generate a random secret key using openssl
#echo "Generating SECRET_KEY for Superset..."
SET_SECRET_KEY="f201a0a4804c9d9b35d4d043b5acf2fefc540a07b663553cc4b8dc787cef42dd"

#set the path for SUPERSET_CONFIG

# Create Superset configuration file with the generated SECRET_KEY
echo "Creating Superset configuration file..."
cat <<EOL > ~/superset_config.py
from cachelib.redis import RedisCache
from celery.schedules import crontab

# PostgreSQL as the metadata database
SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://superset_prod_user:superset_password@localhost/superset_prod_db'

# Redis configuration for caching
CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_DEFAULT_TIMEOUT': 300,
    'CACHE_KEY_PREFIX': 'superset_',
    'CACHE_REDIS_HOST': 'localhost',
    'CACHE_REDIS_PORT': 6379,
    'CACHE_REDIS_DB': 0,
    'CACHE_REDIS_URL': 'redis://localhost:6379/0'
}

DATA_CACHE_CONFIG = CACHE_CONFIG

# Celery configuration for async tasks
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

# Schedule periodic tasks
CELERY_BEAT_SCHEDULE = {
    'reports.scheduler': {
        'task': 'superset.tasks.scheduler.run_scheduled_reports',
        'schedule': crontab(minute='*/1'),
    }
}

# Secret Key for signing cookies
SECRET_KEY = "$SET_SECRET_KEY"
EOL

export SUPERSET_CONFIG_PATH=~/superset_config.py

# Initialize Superset database
echo "Initializing Superset database..."
export FLASK_APP=superset
superset db upgrade

# Create admin user for Superset
echo "Creating admin user for Superset..."
superset fab create-admin \
    --username admin \
    --firstname Admin \
    --lastname User \
    --email admin@example.com \
    --password admin

# Initialize Superset application
echo "Initializing Superset application..."
superset init

#Load examples sets
#superset load_examples

# Create systemd service for Gunicorn (Superset)
echo "Creating Gunicorn systemd service for Superset..."
cat <<EOL | sudo tee /etc/systemd/system/superset.service
[Unit]
Description=Gunicorn instance to serve Superset
After=network.target

[Service]
User=$USER
Group=www-data
WorkingDirectory=/home/$USER
ExecStart=/usr/local/bin/gunicorn -w 4 -b 0.0.0.0:8088 'superset.app:create_app()'

[Install]
WantedBy=multi-user.target
EOL

# Reload systemd, start, and enable Superset service
echo "Starting Superset service..."
sudo systemctl daemon-reload
sudo systemctl start superset
sudo systemctl enable superset

# Create systemd service for Celery Worker
echo "Creating Celery Worker systemd service..."
cat <<EOL | sudo tee /etc/systemd/system/celery-worker.service
[Unit]
Description=Superset Celery Worker
After=network.target

[Service]
User=$USER
Group=www-data
WorkingDirectory=/home/$USER
ExecStart=/usr/local/bin/celery worker --app=superset.tasks.celery_app:app --loglevel=INFO

[Install]
WantedBy=multi-user.target
EOL

# Create systemd service for Celery Beat
echo "Creating Celery Beat systemd service..."
cat <<EOL | sudo tee /etc/systemd/system/celery-beat.service
[Unit]
Description=Superset Celery Beat Service
After=network.target

[Service]
User=$USER
Group=$USER
WorkingDirectory=/home/$USER
ExecStart=/usr/local/bin/celery beat --app=superset.tasks.celery_app:app --loglevel=INFO

[Install]
WantedBy=multi-user.target
EOL

# Reload systemd, start, and enable Celery services
echo "Starting Celery Worker and Beat services..."
sudo systemctl daemon-reload
sudo systemctl start celery-worker
sudo systemctl start celery-beat
sudo systemctl enable celery-worker
sudo systemctl enable celery-beat

domname=`hostname`

# Configure Nginx as a reverse proxy
echo "Configuring Nginx as a reverse proxy..."
sudo tee /etc/nginx/conf.d/superset.conf <<EOL
server {
    listen 80;
    server_name $domname;

    location / {
        proxy_pass http://127.0.0.1:8088;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOL

# Start and enable Nginx
echo "Starting and enabling Nginx..."
sudo systemctl restart nginx
sudo systemctl enable nginx

# Optionally enable SSL with Let's Encrypt (run manually)
# sudo dnf install certbot python3-certbot-nginx
# sudo certbot --nginx -d yourdomain.com

echo "Apache Superset installation completed successfully!"
echo "Access Superset at http://$domname or http://localhost"