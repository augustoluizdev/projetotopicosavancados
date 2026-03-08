---

# Sistema de Gerenciamento de Eventos

Um sistema de gerenciamento de eventos baseado em **Django**, construído seguindo os princípios da **Clean Architecture**.

---

# Arquitetura

Este projeto segue a **Clean Architecture** com as seguintes camadas:

* **Domain (Domínio)**: Entidades principais do negócio e regras de negócio
* **Application (Aplicação)**: Casos de uso e lógica da aplicação
* **Infrastructure (Infraestrutura)**: Elementos externos (banco de dados, frameworks, etc.)
* **Presentation (Apresentação)**: API e interfaces de usuário

---

# Funcionalidades

* Criar e gerenciar eventos
* Registrar participantes em eventos
* Listar eventos e participantes
* Gerenciar o status dos eventos (Rascunho, Publicado, Cancelado, Concluído)

---

# Estrutura do Projeto

```
├── src/
│   ├── domain/                 # Camada de Domínio
│   │   ├── entities/          # Entidades de negócio
│   │   ├── value_objects/     # Objetos de valor
│   │   └── exceptions/        # Exceções do domínio
│
│   ├── application/           # Camada de Aplicação
│   │   ├── dto/              # Objetos de transferência de dados
│   │   ├── ports/            # Interfaces abstratas
│   │   └── use_cases/        # Casos de uso do negócio
│
│   ├── infrastructure/        # Camada de Infraestrutura
│   │   ├── django_app/       # Models e admin do Django
│   │   ├── repositories/     # Implementações de repositórios
│   │   └── config/           # Injeção de dependências
│
│   └── presentation/         # Camada de Apresentação
│       └── api/              # API REST
│
├── tests/                     # Testes do projeto
├── config/                    # Configurações do Django
├── manage.py                  # Script de gerenciamento do Django
└── pyproject.toml             # Dependências do projeto
```

---

# Configuração (Setup)

### 1️⃣ Instalar dependências

```bash
pip install -e .
```

### 2️⃣ Executar as migrações do banco de dados

```bash
python manage.py migrate
```

### 3️⃣ Rodar o servidor de desenvolvimento

```bash
python manage.py runserver
```

---

# Endpoints da API

## Eventos

* `GET /api/events/` → Listar todos os eventos
* `POST /api/events/create/` → Criar um novo evento
* `GET /api/events/{id}/` → Obter detalhes de um evento

---

## Participantes

* `POST /api/participants/register/` → Registrar participação em um evento
* `GET /api/events/{id}/participants/` → Listar participantes de um evento

---

# Testes

Para executar os testes:

```bash
pytest
```

---

# Desenvolvimento

Este projeto segue os princípios da **Clean Architecture**:

* **Regra de Dependência**: Camadas internas não dependem de camadas externas
* **Abstração**: Interfaces definem contratos entre as camadas
* **Injeção de Dependência**: Dependências são injetadas, não codificadas diretamente
* **Responsabilidade Única**: Cada classe tem apenas uma responsabilidade

---

# Licença

Licença MIT

---
