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

### Track views

To can track on every web framework with ease, **fastrack doesn't track automatically**, instead of this here you have recipes for your favourite front taste. 

#### VanillaJS

```js
window.addEventListener('beforeunload', window.fastrack_trackview);
```
When `beforeunload` event is triggered, you can use `fastrack_trackview()` function to track the current page and time spent on it.

#### Vue

```js
var first_load = true
router.beforeEach((from, to, next) => {
    if (first_load) {
        first_load = false
    } else {
        window.fastrack_trackview()
    }
    return next() 
})
```
Thanks to router guards we can control how to track, but it always launch `beforeEach` guard at the begining so we need to flag the first call.

### Identify users

To assign collected info to an email, we can use the function `fastrack_identify(email)` when he login, add the email in a form or something to relate this email with fastrack tracker variables.


### Metadata

When `fastrack_trackview()` is called, it will do a request to track some variables automatically but you can add custom data for your bussiness logic using `window.fastrack_metadata = {"myobject": "for view A", "is": ["a", "standard", "json"]}`

### Use collected data 

Here we have 3 ways to deep into:

*  Use directly the postgres DB with tools like **Metabase** to accesss and filter
*  Use `python manage.py shell` and query with **Django ORM**
*  Use `/track?email=<email to get tracking>` to get his navigation history (to use it we must define a SECURITY KEY)

### Add security key

In the environment file (`.env`) add:

```
PRIVATE_ACCESS_KEYS=mykeys,areseparated,bycommas
```

and then use one of the defined keys as header `x-access-key`

```
curl -X GET "<fastrackendpoint>/track?email=myemail%40email.com" -H  "accept: application/json" -H  "x-access-key: mykeys"
```
