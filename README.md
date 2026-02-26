## Prerequisites

| Component | Version     | Installation Link |
|-----------|-------------|------------------|
| Python | 3.10+       | [Download](https://python.org) |
| Node.js | 20.19+      | [Download](https://nodejs.org) |
| PostgreSQL | 16+         | [Download](https://postgresql.org) |
| OSGeo4W | Latest(312) | [Download](https://trac.osgeo.org/osgeo4w/) |



```bash
gis_monitoring/
├── backend/
│   ├── apps/
│   │   ├── users/          # User authentication & profiles
│   │   ├── objects/        # Geospatial objects monitoring
│   ├── config/             # Django settings (settings.py, urls.py, etc.)
│   ├── .env                # Backend environment variables (DO NOT COMMIT)
│   ├── .env.example        # Template for .env
│   ├── manage.py           # Django management script
│   └── requirements.txt    # Python dependencies
│
├── frontend/
│   ├── src/
│   │   ├── api/            # API client (now in stores)
│   │   ├── components/     # Vue components
│   │   ├── stores/         # Pinia stores
│   │   └── App.vue
│   ├── public/
│   ├── .env                # Frontend environment variables (DO NOT COMMIT)
│   ├── .env.example        # Template for .env
│   ├── package.json
│   └── vite.config.ts
│
├── README.md
└── .gitignore
```

### Database Setup
#### 1. Install PostgreSQL with PostGIS
Windows:
 - Download [postgresql.org](https://www.postgresql.org/download/windows/?spm=a2ty_o01.29997173.0.0.44de5171t4iMGW)
  - During installation, enable PostGIS extension!!!
  
Linux:
```bash
sudo apt install postgresql postgresql-contrib postgis postgresql-16-postgis-3
```
#### 2. Create Database
```bash
psql -U postgres

CREATE USER gis_user WITH PASSWORD 'your_secure_password';

CREATE DATABASE gis_monitoring OWNER gis_user;

\c gis_monitoring

CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;

GRANT ALL PRIVILEGES ON SCHEMA public TO gis_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO gis_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO gis_user;

ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO gis_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO gis_user;
```

```bash
# Verify PostGIS
SELECT PostGIS_Version();
```
 
### Backend Setup
#### 1. Navigate to Backend Directory
```bash
cd backend
```
#### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```
#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```
#### 4. GIS Configuration (Windows Only)
- Download from https://trac.osgeo.org/osgeo4w/
- Run installer, select Advanced Install
- Install packages: [gdal], [geos], [proj]
- Note installation path

#### 5. Configure Environment Variables
```bash
# Copy template
cp .env.example .env

# Edit .env with your settings (see Environment Variables section)
```
Create a new secret key:
```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```
#### 6. Migrations
```bash
python manage.py makemigrations users 
python manage.py makemigrations objects
python manage.py migrate
```

#### 7. Create Superuser
```bash
python manage.py createsuperuser
```
#### 8. Start Backend Server
```bash
python manage.py runserver
```
Backend will be available at: http://localhost:8000

### Frontend Setup

#### 1. install 
```bash
cd frontend
```
```bash
npm install
```

```bash
# if necessary:
npm audit fix 
```
#### 2. Configure Environment Variables
```bash
# Copy template
cp .env.example .env

# Edit .env with your settings (see Environment Variables section)
```
#### 3. Start Development Server
```bash
npm run dev
```

Frontend will be available at: http://localhost:5173