# Notification Worker Lab

Sistema de notificações assíncronas com **FastAPI**, **Redis**, **RabbitMQ**, **PostgreSQL** e um **Worker** de processamento.

## Arquitetura

```
┌──────────┐    POST /notifications    ┌───────────┐    publish    ┌────────────┐
│  Client  │ ───────────────────────►  │  FastAPI   │ ──────────►  │  RabbitMQ  │
└──────────┘                           │    API     │              └─────┬──────┘
                                       └──┬────┬───┘                    │
                                     save │    │ emit                   │ consume
                                          ▼    ▼                        ▼
                                    ┌───────┐ ┌──────────┐       ┌────────────┐
                                    │ Redis │ │ Postgres │ ◄──── │   Worker   │
                                    │ cache │ │  ledger  │ emit  │            │
                                    └───────┘ └──────────┘       └─────┬──────┘
                                        ▲                              │
                                        └──────────────────────────────┘
                                                    update
```

**Redis** = cache/projection (estado atual da notificação, leitura rápida)
**PostgreSQL** = ledger append-only (histórico completo de eventos)

## Ledger com PostgreSQL

Os eventos da notificação são persistidos em uma tabela append-only no PostgreSQL.
Redis é usado apenas como cache/projection para leitura rápida do estado atual.

**Fluxo de eventos:**

```
created → processing → sent/failed
```

Cada mudança de status gera um evento imutável no ledger:

```json
[
  { "event_type": "notification.created",    "event_version": 1, "payload": { "status": "pending" } },
  { "event_type": "notification.processing", "event_version": 1, "payload": { "status": "pending" } },
  { "event_type": "notification.sent",       "event_version": 1, "payload": { "status": "sent" } }
]
```

**Tabela:**

```sql
CREATE TABLE notification_events (
    id              UUID PRIMARY KEY,
    notification_id UUID NOT NULL,
    event_type      VARCHAR(50)  NOT NULL,
    event_version   INTEGER      NOT NULL DEFAULT 1,
    payload         JSONB        NOT NULL DEFAULT '{}',
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);
```

**Consultar eventos:**

```bash
curl http://localhost:8000/api/notifications/{id}/events
```

## Estrutura do Projeto

```
app/
├── config/             # Configurações (variáveis de ambiente)
├── domain/
│   ├── entities/       # Notification, NotificationEvent
│   ├── enums/          # NotificationStatus, NotificationEventType
│   ├── repositories/   # Interfaces abstratas (ABC)
│   └── services/       # Lógica de negócio
├── application/
│   ├── dto/            # Input/Output models (Pydantic)
│   └── use_cases/      # Casos de uso (create, get)
├── infra/
│   ├── redis/          # Repositório de notificações (cache)
│   ├── postgres/       # Repositório de eventos (ledger)
│   ├── rabbitmq/       # Publisher e Consumer
│   └── workers/        # Notification Worker
├── presentation/
│   └── api/
│       ├── routes/     # Endpoints FastAPI
│       ├── schemas/    # Request/Response schemas
│       └── dependencies.py
└── main.py             # App FastAPI
```

## Requisitos

- Docker e Docker Compose

## Como Executar

```bash
docker compose up --build -d
```

Isso sobe 5 containers:

| Serviço      | Porta          | Descrição                |
|--------------|----------------|--------------------------|
| **api**      | 8000           | API FastAPI              |
| **worker**   | —              | Consumer RabbitMQ        |
| **redis**    | 6379           | Cache/projection         |
| **postgres** | 5432           | Ledger de eventos        |
| **rabbitmq** | 5672 / 15672   | Fila + Management UI     |

## Endpoints

### Health Check

```bash
curl http://localhost:8000/health
```

### Criar Notificação

```bash
curl -X POST http://localhost:8000/api/notifications/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Alerta", "message": "Servidor reiniciado"}'
```

### Buscar por ID

```bash
curl http://localhost:8000/api/notifications/{id}
```

### Listar Todas

```bash
curl http://localhost:8000/api/notifications/
```

### Filtrar por Status

```bash
curl http://localhost:8000/api/notifications/status/sent
```

Status disponíveis: `pending`, `sent`, `failed`

### Auditoria — Eventos de uma Notificação

```bash
curl http://localhost:8000/api/notifications/{id}/events
```

Retorna o histórico completo de eventos (ledger) ordenados cronologicamente.

## RabbitMQ Management

Acesse o painel em [http://localhost:15672](http://localhost:15672) com `guest` / `guest`.

## Variáveis de Ambiente

| Variável | Default | Descrição |
|----------|---------|-----------|
| `REDIS_HOST` | `localhost` | Host do Redis |
| `REDIS_PORT` | `6379` | Porta do Redis |
| `REDIS_PASSWORD` | — | Senha do Redis |
| `POSTGRES_HOST` | `localhost` | Host do PostgreSQL |
| `POSTGRES_PORT` | `5432` | Porta do PostgreSQL |
| `POSTGRES_USER` | `notification` | Usuário PostgreSQL |
| `POSTGRES_PASSWORD` | `notification` | Senha PostgreSQL |
| `POSTGRES_DB` | `notification_db` | Nome do banco |
| `RABBITMQ_HOST` | `localhost` | Host do RabbitMQ |
| `RABBITMQ_PORT` | `5672` | Porta do RabbitMQ |
| `RABBITMQ_USERNAME` | `guest` | Usuário RabbitMQ |
| `RABBITMQ_PASSWORD` | `guest` | Senha RabbitMQ |
| `RABBITMQ_VHOST` | `/` | Virtual host |
| `RABBITMQ_QUEUE` | `notifications` | Nome da fila |
| `RABBITMQ_EXCHANGE` | `notifications_exchange` | Nome do exchange |
| `RABBITMQ_ROUTING_KEY` | `notification.created` | Routing key |

## Teste de Idempotência

Foi executado um stress test publicando 100 mensagens duplicadas no RabbitMQ com o mesmo `notification_id`.

Resultado:

- 100 mensagens publicadas
- 1 notificação processada
- 99 mensagens ignoradas como duplicadas
- status final da notificação: `sent`

Isso valida que o Worker está preparado para o modelo de entrega `at least once`, evitando reprocessamento indevido.

## Parar os Containers

```bash
docker compose down
```

Para remover volumes (dados do Redis, PostgreSQL e RabbitMQ):

```bash
docker compose down -v
```
