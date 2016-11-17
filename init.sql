CREATE TABLE users(
    id SERIAL PRIMARY KEY,                                                                                                                        
    username varchar(20),
    password varchar(100)
);

CREATE TABLE comments(
    user_id integer REFERENCES users (id),
    text varchar(500)
);
