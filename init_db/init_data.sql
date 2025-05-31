CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
-- Insert Users
INSERT INTO user_db (id, name, email) VALUES
(uuid_generate_v4(), 'Alice Johnson', 'alice@example.com'),
(uuid_generate_v4(), 'Bob Smith', 'bob@example.com'),
(uuid_generate_v4(), 'Charlie Rose', 'charlie@example.com')
ON CONFLICT (id) DO NOTHING;

-- Insert Movies
INSERT INTO movie_db (id, title, description) VALUES
(uuid_generate_v4(), 'The Matrix', 'A hacker discovers the shocking truth about reality.'),
(uuid_generate_v4(), 'Inception', 'A thief who steals corporate secrets through dream-sharing technology.'),
(uuid_generate_v4(), 'Interstellar', 'A team of explorers travel through a wormhole in space.')
ON CONFLICT (id) DO NOTHING;

-- Insert Ratings
INSERT INTO rating_db (id, user_id, movie_id, rating)
SELECT
    uuid_generate_v4(),
    u.id,
    m.id,
    5
FROM user_db u, movie_db m
ON CONFLICT (id) DO NOTHING;
