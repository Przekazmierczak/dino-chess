# Dino Chess - Django Chess App

Dino Chess is a full-stack, real-time chess platform built with Django. Whether you're facing a friend or challenging the AI, Dino Chess offers a secure, and responsive gameplay experience—deployed with Docker, hosted on AWS, and optimized through Cloudflare.

#### To test the app visit: [dino-chess.com](https://dino-chess.com/)

![dinochess1](https://github.com/user-attachments/assets/9cebe2ff-fb38-4cdb-a229-57f67efda104)

## Features

- Play chess in real time against other users
- Play against AI (powered by Stockfish engine)
- User authentication (login and registration)
- Responsive user interface (works on desktop, tablet, and mobile)
- Real-time gameplay via WebSockets
- Full chess rules support:
  - Legal move validation
  - Castling
  - En passant
  - Pawn promotion
  - Check, checkmate, and draw conditions
- Track game and board history move-by-move
- Background task processing with Celery and Redis
- Dockerized setup for local development and production
- Deployed on AWS with security and performance via Cloudflare
- Unit tested with Python unittest
- NGINX as reverse proxy and static file handler

## Tech Stack

### Backend:
- Django
- SQLite
- Celery
- Redis
- Daphne (ASGI server)
- Stockfish (chess AI engine)

### Frontend:
- HTML
- CSS
- JavaScript (dynamic game board + WebSocket integration)

### Infrastructure:
- Docker
- NGINX
- AWS (EC2, ECR)
- Cloudflare

## Deployment

This app is deployed using:
- Docker + Docker Compose
- AWS EC2 for backend hosting
- NGINX for reverse proxy/static handling
- Cloudflare for DNS, SSL, and performance optimization

## AI (Stockfish) Integration

- Stockfish chess engine is integrated and communicates via Python subprocess and Celery as background tasks.
- The AI can be configured for different levels of difficulty.
- All legal moves are validated against both the AI and user inputs before execution.

## Legal Move Validation

The application enforces full chess rules including:
- Move legality
- Special moves:
  - Castling
  - En passant
  - Pawn promotion
  - Detection of check, checkmate, and stalemate
  - Game-ending conditions
  - Full board history tracking for replay and analysis

## Responsive Design

Fully responsive layout using CSS media queries
Optimized for mobile phones, tablets, and desktop screens
Game board adjusts automatically to screen size for better user experience

## Requirements

### Python Dependencies:
- celery==5.4.0 – Task queue for background jobs
- channels==4.0.0 – WebSocket support for Django
- channels-redis==4.2.0 – Redis backend for Channels
- daphne==4.1.2 – ASGI server for Django
- Django==5.0.2 – Core web framework
- fakeredis==2.23.2 – Redis mock for testing
- gunicorn==21.2.0 – WSGI HTTP server for Django
- pytest==8.2.1, pytest-asyncio==0.23.7 – Testing tools
- redis==5.0.4 – Python Redis client
- selenium==4.18.1 – End-to-end testing
- stockfish==3.28.0 – Stockfish AI wrapper
- websocket-client==1.8.0, websockets==13.0.1 – WebSocket handling

### System Requirements:
- Docker – For containerizing the app and its services using docker-compose
- Redis Server – Message broker for Celery and WebSocket layer
- NGINX – Reverse proxy server:
  - Routes HTTP/WebSocket traffic to Daphne/Gunicorn
  - Serves static/media files
  - Can handle SSL/TLS termination (or be combined with Cloudflare)

## Usage

1. Clone the repository or copy the project files to your local machine.
2. Run Docker
3. Open a terminal and navigate to the project directory.

To build the project, run:

```bash
docker-compose up --build
```

Visit the app at:

```browser
http://localhost
```

To stop the project, run:

```bash
docker-compose down
```

## File Structure

```
django-chess/
│
├── chess_django/                  # Main Django project folder
│   └── chess_django/              # Django settings and core configuration
│   └── lobby/                     # App handling game lobbies and matchmaking
│   └── menu/                      # App for navigation, main menu UI
│   └── play_with_computer/        # App for playing chess against the Stockfish AI
│   └── table/                     # App managing the game board and multiplayer logic
│   └── manage.py                  # Django management script
│
├── nginx/                         # NGINX configuration for reverse proxy
│   └── Dockerfile                 # Dockerfile for building the NGINX container
│   └── mime.types                 # MIME type declarations for NGINX
│   └── nginx.conf                 # Main NGINX configuration file
│
├── .dockerignore                  # Docker ignore rules
├── .gitignore                     # Git ignore rules
├── docker-compose.yml             # Docker Compose configuration for all services
├── Dockerfile                     # Dockerfile for the Django application
├── LICENSE                        # License file
├── README.md                      # Project documentation
└── requirements.txt               # Python dependencies
```

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Contact

For issues or suggestions:
- GitHub
- Email: prze.kazmierczak@gmail.com
