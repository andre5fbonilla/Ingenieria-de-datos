-- Crear tabla principal (Posts)
CREATE FUNCTION get_post_day(post_timestamp TIMESTAMP) RETURNS VARCHAR(20) AS $$
BEGIN
    RETURN TO_CHAR(post_timestamp, 'Day');
END;
$$ LANGUAGE plpgsql IMMUTABLE;


CREATE TABLE posts (
    post_ID VARCHAR(50) PRIMARY KEY,
    platform VARCHAR(50),
    post_type VARCHAR(50),
    post_content TEXT,
    post_timestamp TIMESTAMP,
	post_date DATE GENERATED ALWAYS AS (DATE(post_timestamp)) STORED,
	post_day VARCHAR(20) GENERATED ALWAYS AS (get_post_day(post_timestamp)) STORED,
	post_period_time VARCHAR(20) GENERATED ALWAYS AS (CASE 
                    WHEN EXTRACT(hour FROM post_timestamp) >= 6 AND EXTRACT(hour FROM post_timestamp) < 12 THEN 'Morning'
                    WHEN EXTRACT(hour FROM post_timestamp) >= 12 AND EXTRACT(hour FROM post_timestamp) < 18 THEN 'Afternoon'
                    WHEN ((EXTRACT(hour FROM post_timestamp) >= 18 AND EXTRACT(hour FROM post_timestamp) < 24) OR (EXTRACT(hour FROM post_timestamp) <6))THEN 'Night'
                    ELSE 'Night'
                END) STORED,
    campaign_ID VARCHAR(50),
    sentiment VARCHAR(50),
    influencer_ID VARCHAR(50)
);

-- Crear tabla de indicadores (Indicators)
CREATE TABLE indicators (
    indicators_ID INT PRIMARY KEY,
    post_ID VARCHAR(50),
    likes INT,
    num_comments INT,
    shares INT,
    impressions INT,
    reach INT,
    engagement_rate FLOAT,
    FOREIGN KEY (post_ID) REFERENCES posts(post_ID)
);

-- Crear tabla de Audiencia (Audience)
CREATE TABLE Audience (
    audience_ID INT PRIMARY KEY,
    post_ID VARCHAR(50),
    audience_age INT,
    age_group VARCHAR(50),
    audience_gender VARCHAR(50),
    audience_location VARCHAR(100),
    audience_continent VARCHAR(50),
    audience_interests VARCHAR(50),
    FOREIGN KEY (post_ID) REFERENCES posts(post_ID)
);

--Insertar datos en la tabla Posts
copy Posts
from 'C:/Users/juand/OneDrive/Desktop/csv/posts.csv'
with delimiter as ';' csv HEADER;

--Insertar datos en la tabla Indicators
copy Indicators
from 'C:/Users/juand/OneDrive/Desktop/csv/indicators.csv'
with delimiter as ';' csv HEADER;

--Insertar datos en la tabla Audience
copy Audience
from 'C:/Users/juand/OneDrive/Desktop/csv/audience.csv'
with delimiter as ';' csv HEADER;

--Creacion del usuario
CREATE USER usuario_posts WITH PASSWORD '123456';
GRANT SELECT ON ALL TABLES IN SCHEMA public TO usuario_posts;


