CREATE SCHEMA IF NOT EXISTS content;

CREATE TABLE "content"."career" (
    "id" uuid NOT NULL PRIMARY KEY,
    "name" text NOT NULL,
    "created_at" timestamp with time zone NOT NULL,
    "updated_at" timestamp with time zone NOT NULL
    );

CREATE TABLE "content"."filmwork_type" (
    "id" uuid NOT NULL PRIMARY KEY,
    "name" text NOT NULL,
    "created_at" timestamp with time zone NOT NULL,
    "updated_at" timestamp with time zone NOT NULL
    );

CREATE TABLE "content"."filmwork" (
    "id" uuid NOT NULL PRIMARY KEY,
    "title" text NOT NULL,
    "description" text NOT NULL,
    "creation_date" date NULL,
    "certificate" text NOT NULL DEFAULT '',
    "file_path" text NOT NULL DEFAULT '',
    "rating" double precision NULL,
    "type_id" uuid NOT NULL REFERENCES "content"."filmwork_type" DEFERRABLE INITIALLY DEFERRED,
    "created_at" timestamp with time zone NOT NULL,
    "updated_at" timestamp with time zone NOT NULL
    );

CREATE TABLE "content"."genre" (
    "id" uuid NOT NULL PRIMARY KEY,
    "name" text NOT NULL,
    "description" text NOT NULL DEFAULT '',
    "created_at" timestamp with time zone NOT NULL,
    "updated_at" timestamp with time zone NOT NULL
    );

CREATE TYPE gender as ENUM('male', 'female', '');
CREATE TABLE "content"."person" (
    "id" uuid NOT NULL PRIMARY KEY,
    "full_name" text NOT NULL,
    "birth_day" date NULL,
    "gender" gender NULL,
    "created_at" timestamp with time zone NOT NULL,
    "updated_at" timestamp with time zone NOT NULL
    );

CREATE TABLE "content"."careers_persons" (
    "id" uuid NOT NULL PRIMARY KEY,
    "career_id" uuid NOT NULL REFERENCES "content"."career" ON DELETE RESTRICT ON UPDATE CASCADE DEFERRABLE INITIALLY DEFERRED,
    "person_id" uuid NOT NULL REFERENCES "content"."person" ON DELETE CASCADE ON UPDATE CASCADE DEFERRABLE INITIALLY DEFERRED,
    "date_start" date NULL,
    "date_finish" date NULL,
    "created_at" timestamp with time zone NOT NULL,
    UNIQUE("person_id", "career_id")
    );

CREATE TABLE "content"."persons_filmworks" (
    "id" uuid NOT NULL PRIMARY KEY,
    "filmwork_id" uuid NOT NULL REFERENCES "content"."filmwork" ON DELETE CASCADE ON UPDATE CASCADE DEFERRABLE INITIALLY DEFERRED,
    "person_id" uuid NOT NULL REFERENCES "content"."person" ON DELETE CASCADE ON UPDATE CASCADE DEFERRABLE INITIALLY DEFERRED,
    "role_id" uuid NOT NULL REFERENCES "content"."career" ON DELETE RESTRICT ON UPDATE CASCADE DEFERRABLE INITIALLY DEFERRED,
    "created_at" timestamp with time zone NOT NULL,
    UNIQUE("filmwork_id", "person_id", "role_id")
    );

CREATE TABLE "content"."genres_filmworks" (
    "id" uuid NOT NULL PRIMARY KEY,
    "genre_id" uuid NOT NULL REFERENCES "content"."genre" ON DELETE RESTRICT ON UPDATE CASCADE DEFERRABLE INITIALLY DEFERRED,
    "filmwork_id" uuid NOT NULL REFERENCES "content"."filmwork" ON DELETE CASCADE ON UPDATE CASCADE DEFERRABLE INITIALLY DEFERRED,
    "created_at" timestamp with time zone NOT NULL,
    UNIQUE("filmwork_id", "genre_id")
    );

CREATE INDEX "persons_filmworks_person_id_561d0ff6" ON "content"."persons_filmworks" ("person_id");
