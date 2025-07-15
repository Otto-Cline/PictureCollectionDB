CREATE TABLE IF NOT EXISTS collections (
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE
);

CREATE TABLE IF NOT EXISTS images (
    id SERIAL PRIMARY KEY,
    title VARCHAR,
    creator VARCHAR,
    date VARCHAR,
    source_url VARCHAR,
    collection_id INTEGER REFERENCES collections(id)
);

CREATE TABLE IF NOT EXISTS tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE
);

CREATE TABLE IF NOT EXISTS image_tag (
    image_id INTEGER REFERENCES images(id),
    tag_id INTEGER REFERENCES tags(id),
    PRIMARY KEY (image_id, tag_id)
);