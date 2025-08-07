# voice-rag

## Architecture Diagram

```mermaid
flowchart TD
    User[👤 User]
    UI[UI Service<br/>Streamlit]
    GW[Gateway Service<br/>Entry Point]
    
    FP[RAG File Processing<br/>File Ingestion]
    RR[RAG Retriever<br/>Retrieval]
    
    LLM[LLM Service<br/>Ollama]
    STT[Speech-To-Text<br/>Voice Recognition]
    TTS[Text-To-Speech<br/>Voice Synthesis]
    
    DB[Database<br/>ChromaDB + SQLite]
    
    %% PDF Upload Flow
    User -->|Upload PDF| UI
    UI -->|POST ingest| GW
    GW -->|Process file| FP
    FP -->|Request summary| LLM
    LLM -->|Return summary| FP
    FP -->|Save data| DB
    
    %% Voice Query Flow
    User -->|Record audio| UI
    UI -->|POST query| GW
    GW -->|Convert audio| STT
    STT -->|Transcribed text| GW
    GW -->|Send query| RR
    RR -->|Search context| DB
    DB -->|Similar chunks| RR
    RR -->|Query + context| LLM
    LLM -->|Text response| RR
    RR -->|Convert to audio| TTS
    TTS -->|Audio response| RR
    RR -->|Final audio| GW
    GW -->|Send response| UI
    UI -->|Play audio| User