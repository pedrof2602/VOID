Optimizing cognitive load through a screen-less, context-aware agentic interface.

Technical Overview
Modern Graphical User Interfaces (GUIs) introduce high cognitive friction for executive tasks, forcing users to translate abstract intent into a rigid sequence of visual interactions. VOID resolves this inefficiency by operating as a "Headless Chief of Staff".

By relying entirely on asynchronous audio input and wearable hardware integrations, VOID bypasses the screen. It utilizes a deterministic semantic routing engine to map spoken intent directly to autonomous tool execution. The system is designed to ingest context, orchestrate APIs, and execute commands in the background, returning haptic feedback rather than verbose conversational responses.

System Architecture
The architecture prioritizes low latency and strict separation of concerns between the hardware interception layer, the reasoning engine, and external state mutations.

    subgraph Client [Mobile Client - Flutter]
        H[Hardware / Headset] -->|Button Event| A[Audio Service]
        A -->|Audio Stream| STT[STT Engine]
        HF[Haptic Feedback]
    end

    subgraph Backend [API Gateway - FastAPI]
        STT -->|Transcript| API[REST Endpoint]
        API --> R[DSPy Semantic Router]
    end

    subgraph Intelligence [Reasoning & Tool Execution]
        R -->|Classify: SAVE| M_W[Memory Write]
        R -->|Classify: ACTION| T[Tool Executor]
        R -->|Classify: QUERY| M_R[Memory Read & TTS]
    end

    subgraph Infrastructure [Data & External APIs]
        M_W --> DB[(Supabase / pgvector)]
        M_R --> DB
        T --> DB
        T --> EXT[External APIs e.g., GCalendar]
    end

    T -->|Status 200| API
    M_W -->|Status 200| API
    API -->|Response Trigger| HF
Key Architectural Decisions
1. Backend: Python & FastAPI
Chosen for its native asynchronous capabilities (asyncio) and first-class support for the modern AI ecosystem. FastAPI provides high-throughput request handling necessary for near real-time voice processing, while seamlessly integrating with Google GenAI SDKs and DSPy for LLM orchestration.

2. Client: Flutter & Native Method Channels
Flutter delivers high-fidelity UI for the initial setup while allowing deep native integration. The use of background audio services (audio_service) enables the app to run headlessly, intercepting physical headset button presses to trigger recording loops even when the device is locked or the screen is off.

3. State & Memory: Supabase (PostgreSQL + pgvector)
Memory is handled via PostgreSQL utilizing the pgvector extension. By embedding user inputs into 768-dimensional Matryoshka representations, VOID establishes a long-term semantic memory. This enables Retrieval-Augmented Generation (RAG) for implicit context injection—allowing the agent to fill missing variables in user commands without requesting verbal clarification.

Core Features
Silent Execution Protocol: VOID defaults to action. Commands that result in tool execution or memory ingestion return silent HTTP 200 statuses mapped to physical haptic feedback on the user's device, eliminating unnecessary Text-to-Speech (TTS) latency.

Compiled Semantic Routing (DSPy): Replaces brittle if/else intent parsing and raw prompting with a compiled, probabilistic reasoning engine (ChainOfThought). The router deterministically categorizes inputs into ACTION, MEMORY_WRITE, or MEMORY_READ.

Gap-Filling Autonomous Execution: Before executing external APIs (e.g., Google Calendar), the system queries the vector database to inject implicit user context, correcting ambiguities automatically.

Hardware-First Triggering: Full background persistence. Recording cycles are initiated and terminated strictly via Bluetooth/wired headset media buttons.

Installation & Setup
Prerequisites
Docker & Docker Compose

Flutter SDK (>= 3.19.0)

Supabase Project (with pgvector enabled)

Google Gemini API Key

Backend Deployment
Clone the repository and navigate to the backend directory:

git clone https://github.com/your-org/void.git
cd void/backend
Configure environment variables:

cp .env.example .env
# Update GOOGLE_API_KEY, SUPABASE_URL, SUPABASE_KEY
Build and spin up the Docker containers:

docker-compose up --build -d
The API will be available at http://localhost:8000.

Mobile Client Setup
Navigate to the mobile directory:

cd ../mobile_app
Install dependencies:

flutter pub get
Deploy to a physical device (Required for hardware button testing):

flutter run --release
Note: Ensure the backend URL is correctly pointed to your local network IP or tunneling service (e.g., ngrok) in the app configuration.
