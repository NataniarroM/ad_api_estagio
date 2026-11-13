CREATE TABLE curso (
    id_curso INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome_curso VARCHAR(150) NOT NULL,
    nivel VARCHAR(20) NOT NULL
        CHECK (nivel IN ('tecnologo', 'bacharelado', 'licenciatura')),
    ativo BOOLEAN NOT NULL DEFAULT TRUE
);


CREATE TABLE usuario (
    id_usuario INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        firebase_uid VARCHAR(128) NOT NULL UNIQUE, -- Conexão com autenticação do banco
    id_curso INTEGER,

    nome VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL,

    tipo_usuario VARCHAR(20) NOT NULL
        CHECK (tipo_usuario IN ('estudante', 'empresa', 'admin')),

    telefone VARCHAR(20),
    semestre SMALLINT,
    aluno BOOLEAN NOT NULL DEFAULT FALSE,

    situacao_curso VARCHAR(20)
        CHECK (situacao_curso IN ('cursando', 'concluido')),

    eh_entrevistador BOOLEAN NOT NULL DEFAULT FALSE,

    criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_usuario_curso
        FOREIGN KEY (id_curso)
        REFERENCES curso(id_curso)
        ON DELETE SET NULL,

    CONSTRAINT chk_semestre
        CHECK (semestre IS NULL OR semestre > 0)
);


CREATE TABLE empresa (
    id_empresa INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_usuario INTEGER NOT NULL UNIQUE,

    razao_social VARCHAR(150) NOT NULL,
    nome_fantasia VARCHAR(150) NOT NULL,
    cnpj VARCHAR(18) NOT NULL UNIQUE,
    cidade VARCHAR(100) NOT NULL,
    site VARCHAR(255),

    CONSTRAINT fk_empresa_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES usuario(id_usuario)
        ON DELETE RESTRICT
);


CREATE TABLE vaga (
    id_vaga INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_empresa INTEGER NOT NULL,

    titulo VARCHAR(150) NOT NULL,
    descricao TEXT NOT NULL,
    requisitos TEXT,

    modalidade VARCHAR(20) NOT NULL
        CHECK (modalidade IN ('presencial', 'hibrida', 'remota')),

    bolsa NUMERIC(10,2),
    carga_horaria SMALLINT NOT NULL,

    cidade VARCHAR(100) NOT NULL,

    data_publicacao DATE NOT NULL DEFAULT CURRENT_DATE,
    data_limite DATE NOT NULL,

    status_vaga VARCHAR(20) NOT NULL DEFAULT 'publicada'
        CHECK (status_vaga IN ('publicada', 'encerrada', 'em andamento')),

    criada_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_vaga_empresa
        FOREIGN KEY (id_empresa)
        REFERENCES empresa(id_empresa)
        ON DELETE RESTRICT,

    CONSTRAINT chk_bolsa
        CHECK (bolsa IS NULL OR bolsa >= 0),

    CONSTRAINT chk_carga_horaria
        CHECK (carga_horaria > 0),

    CONSTRAINT chk_data_limite
        CHECK (data_limite >= data_publicacao)
);


CREATE TABLE candidatura (
    id_candidatura INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    id_usuario INTEGER NOT NULL,
    id_vaga INTEGER NOT NULL,

    data_candidatura TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    status_candidatura VARCHAR(20) NOT NULL DEFAULT 'enviada'
        CHECK (status_candidatura IN (
            'enviada',
            'em analise',
            'selecionada',
            'rejeitada',
            'desistencia'
        )),

    curriculo_url VARCHAR(500),

    CONSTRAINT fk_candidatura_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES usuario(id_usuario)
        ON DELETE CASCADE,

    CONSTRAINT fk_candidatura_vaga
        FOREIGN KEY (id_vaga)
        REFERENCES vaga(id_vaga)
        ON DELETE CASCADE,

    CONSTRAINT uk_usuario_vaga
        UNIQUE (id_usuario, id_vaga)
);

