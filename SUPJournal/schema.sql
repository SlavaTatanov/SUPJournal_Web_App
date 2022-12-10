CREATE TABLE users
(
	user_id serial PRIMARY KEY,
	login varchar(64) NOT NULL UNIQUE,
	pass text NOT NULL,
	e_mail text NOT NULL UNIQUE
);
CREATE TABLE workout
(
	pk_workout_id serial PRIMARY KEY,
	fk_user_id integer REFERENCES users(pk_user_id) NOT NULL
)