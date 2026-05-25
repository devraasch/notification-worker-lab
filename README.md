# Notification Worker Lab

Sistema de notificações assíncronas com **FastAPI**, **Redis**, **RabbitMQ** e um **Worker** de processamento.

## Arquitetura

```
┌──────────┐    POST /notifications    ┌───────────┐    publish    ┌────────────┐
│  Client  │ ───────────────────────►  │  FastAPI   │ ──────────►  │  RabbitMQ  │
└──────────┘                           │    API     │              └─────┬──────┘
                                       └─────┬─────┘                    │
                                             │ save                     │ consume
                                             ▼                          ▼
                                       ┌───────────┐            ┌────────────┐
                                       │   Redis   │ ◄───────── │   Worker   │
                                       │  (store)  │   update   │            │
                                       └───────────┘            └────────────┘
```

**Fluxo:**
1. O client envia um `POST /api/notifications/` com `title` e `message`
2. A API salva a notificação no Redis com status `pending` e publica uma mensagem no RabbitMQ
3. O Worker consome a fila, busca a notificação no Redis e atualiza o status para `sent`

## Estrutura do Projeto

```
app/
├── config/             # Configurações (variáveis de ambiente)
├── domain/
│   ├── entities/       # Notification (dataclass)
│   ├── enums/          # NotificationStatus
│   ├── repositories/   # Interface abstrata do repositório
│   └── services/       # Lógica de negócio
├── application/
│   ├── dto/            # Input/Output models (Pydantic)
│   └── use_cases/      # Casos de uso (create, get)
├── infra/
│   ├── redis/          # Implementação do repositório com Redis
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

Isso sobe 4 containers:

| Serviço    | Porta  | Descrição                  |
|------------|--------|----------------------------|
| **api**    | 8000   | API FastAPI                |
| **worker** | —      | Consumer RabbitMQ          |
| **redis**  | 6379   | Armazenamento              |
| **rabbitmq** | 5672 / 15672 | Fila + Management UI |

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

## RabbitMQ Management

Acesse o painel em [http://localhost:15672](http://localhost:15672) com `guest` / `guest`.

## Variáveis de Ambiente

| Variável | Default | Descrição |
|----------|---------|-----------|
| `REDIS_HOST` | `localhost` | Host do Redis |
| `REDIS_PORT` | `6379` | Porta do Redis |
| `REDIS_PASSWORD` | — | Senha do Redis |
| `RABBITMQ_HOST` | `localhost` | Host do RabbitMQ |
| `RABBITMQ_PORT` | `5672` | Porta do RabbitMQ |
| `RABBITMQ_USERNAME` | `guest` | Usuário RabbitMQ |
| `RABBITMQ_PASSWORD` | `guest` | Senha RabbitMQ |
| `RABBITMQ_VHOST` | `/` | Virtual host |
| `RABBITMQ_QUEUE` | `notifications` | Nome da fila |
| `RABBITMQ_EXCHANGE` | `notifications_exchange` | Nome do exchange |
| `RABBITMQ_ROUTING_KEY` | `notification.created` | Routing key |

## Parar os Containers

```bash
docker compose down
```

Para remover volumes (dados do Redis e RabbitMQ):

```bash
docker compose down -v
```

## Teste de Idempotência

Foi executado um stress test publicando 100 mensagens duplicadas no RabbitMQ com o mesmo `notification_id`.

Resultado:

- 100 mensagens publicadas
- 1 notificação processada
- 99 mensagens ignoradas como duplicadas
- status final da notificação: `sent`

Isso valida que o Worker está preparado para o modelo de entrega `at least once`, evitando reprocessamento indevido.
