# fastrack

## Installation

Clone the repository

``` Bash 
git clone https://github.com/FJLendinez/fastrack.git
cd fastrack
cp .env_example .env
```

Edit your .env file with custom settings


### Using docker

Just run:
```
docker-compose up -d
docker exec -it fastrack_api python manage.py migrate
```

### Otherwise
install dependencies

```
pip install -r requirements.txt
python manage.py migrate
```

and run

`uvicorn main:app --reload`

## Use

Use `/a.js` endpoint to have the client functionality


