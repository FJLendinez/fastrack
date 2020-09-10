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

To can track on every web framework with ease, **fastrack track automatically** using 

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

Here we have 4 ways to deep into:

*  Use directly the postgres DB with tools like **Metabase** to accesss and filter
*  Use `python manage.py shell` and query with **Django ORM**
*  Use `/track?email=<email to get tracking>` to get his navigation history (to use it we must define a SECURITY KEY)
*  Use `/analytics` endpoint

### Analytics endpoint

This endpoint require this query params:

*  `operations` a comma separated string to define what operations we need (admited values: `max`, `min`, `avg`, `count`) 

    Example: `?operations=max,count`
*  `operation_value` a string to define the database field of the operation

    Example: `?operations=max&operation_value=time_spent` (max of time spent)
*  `groupby` a string to define the database field to group the operation

    Example: `?operations=avg&operation_value=time_spent&groupby=history_uuid` (average of time_spent per history_uuid)
    
*  **database field** you can aditionally add filter for each database field

    Example: `?operations=avg&operation_value=time_spent&groupby=history_uuid&url=/important_page` (average of time_spent per history_uuid on /important_page)
*  **database field with lookup** you can aditionally add lookups for each database field [Admited lookups field](https://docs.djangoproject.com/en/3.0/ref/models/querysets/#field-lookups)

    Example: `?operations=avg&operation_value=time_spent&groupby=history_uuid&url__icontains=/blog/` (average of time_spent per history_uuid on all pages that contains /blog/)
    
*  **field lookup for metadata** we can use lookups to filter metadata 

    Example:
    Supose that we track on metadata {"info": "important"} and {"info": "meh"} on our blog and {"potatoes": "are great"} on another route
    We can use `?operations=avg&operation_value=time_spent&groupby=history_uuid&metadata__info=important` to get the average time spent per history_uuid on pages that have {"info": "important"} on it metadata

### Add security key

In the environment file (`.env`) add:

```
PRIVATE_ACCESS_KEYS=mykeys,areseparated,bycommas
```

and then use one of the defined keys as header `x-access-key`

```
curl -X GET "<fastrackendpoint>/track?email=myemail%40email.com" -H  "accept: application/json" -H  "x-access-key: mykeys"
```
