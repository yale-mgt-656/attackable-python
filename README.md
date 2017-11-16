# Attackable Python

A demo web app that shows "worst practices". The app is vulnerable
to XSS, SQL Injection, and CSRF attacks.

To run the app, you'll need a Postgres database, which you create
using `createdb` and then you'll need to create the schema using
the `init.sql` script. This sequence might be like the following
if you're running postgres on localhost with the default settings
and no need for a password.

```
createdb attackable
psql attackable <init.sql
```

Then, you'd start the web app like

```
DATABASE_URL="postgresql://localhost/attackable" python ./main.py
```
