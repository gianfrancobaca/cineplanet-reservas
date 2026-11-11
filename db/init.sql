CREATE TABLE peliculas (
    id      SERIAL PRIMARY KEY,
    titulo  TEXT NOT NULL
);

CREATE TABLE funciones (
    id           SERIAL PRIMARY KEY,
    pelicula_id  INTEGER NOT NULL REFERENCES peliculas(id),
    sala         TEXT NOT NULL,
    inicio       TIMESTAMPTZ NOT NULL
);

CREATE TABLE asientos (
    id          SERIAL PRIMARY KEY,
    funcion_id  INTEGER NOT NULL REFERENCES funciones(id),
    codigo      TEXT NOT NULL,
    estado      TEXT NOT NULL DEFAULT 'libre'
                CHECK (estado IN ('libre', 'vendido')),
    UNIQUE (funcion_id, codigo)
);

CREATE TABLE ventas (
    id          SERIAL PRIMARY KEY,
    asiento_id  INTEGER NOT NULL REFERENCES asientos(id),
    cliente     TEXT NOT NULL,
    creada_en   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Datos de prueba (inventados, no son de Cineplanet)
INSERT INTO peliculas (titulo) VALUES ('Película de prueba');

INSERT INTO funciones (pelicula_id, sala, inicio)
VALUES (1, 'Sala 1', '2026-11-20 19:30:00-05');

INSERT INTO asientos (funcion_id, codigo)
SELECT 1, fila || numero
FROM unnest(ARRAY['A', 'B']) AS fila,
     generate_series(1, 5) AS numero;