# 🌌 SATORI ECOSYSTEM — MASTER ARCHITECTURE & TASK DOCUMENT

> **"Tarqoq dasturlardan — yagona ongli ekotizim sari."**
>
> **Versiya:** 1.0 | **Sana:** 2026-09-26 | **Muallif:** Bexruz
> **Holat:** 🟡 Faol ishlanmoqda — Phase 1 (Foundation)

---

## 📖 MUNDARIJA

1. [Loyiha Falsafasi](#1-loyiha-falsafasi)
2. [Ekotizimning 4 Ustuni](#2-4-ustun)
3. [Global Arxitektura](#3-global-arxitektura)
4. [Hozirgi Holat (Current State)](#4-hozirgi-holat)
5. [Ma'lumotlar Bazasi Sxemasi](#5-database-schema)
6. [Ichki Protokollar](#6-protokollar)
7. [Xavfsizlik Tamoyillari](#7-xavfsizlik)
8. [📋 IMPLEMENTATION TASK LIST](#8-task-list)
9. [Rivojlanish Xaritasi](#9-roadmap)

---

## 1. Loyiha Falsafasi

**"Satori"** (yaponcha 悟り) — **"to'satdan anglash"**, narsalarning asl mohiyatini to'liq ko'ra olish.

Satori — bu:
- 🏪 **App Distribution Store** — barcha shaxsiy ilovalarni bitta markazga birlashtiruvchi
- 📊 **Unified Activity Logger** — faoliyat loglarini yig'ib tahlil qiluvchi
- 🧠 **Contextual AI Engine** — LLM larga to'liq shaxsiy kontekst beruvchi

### Satori hal qiladigan 3 fundamental muammo

| # | Muammo | Satori yechimi |
|---|--------|----------------|
| 1 | **Amneziyaga uchragan AI** — har yangi chatda o'zingni qayta tanishtirish | Loglar asosida AI avtomatik kontekst biladi (RAG) |
| 2 | **Tarqoq mikro-loyihalar** — har biri alohida auth, DB, AI integratsiyasi | Yagona Hub: App Store + Core API |
| 3 | **Noqulay AI interfeyslari** — brauzerni ochish, ctrl+c/v bilan ishlash | ItachiAsist — OS overlay sifatida har doim tayyor |

---

## 2. 4 Ustun

```
┌─────────────────┬─────────────────┬──────────────────┬──────────────────┐
│  1. APP STORE   │  2. LOG ENGINE  │   3. AI BRAIN    │ 4. AGENT CLIENTS │
│  (Distribution) │  (Telemetry)    │  (Context & LLM) │  (ItachiAsist)   │
├─────────────────┼─────────────────┼──────────────────┼──────────────────┤
│ • Ilovalar      │ • Tizim va App  │ • RAG & Vektor   │ • C# Avalonia UI │
│   katalogi      │   loglarini     │   xotira         │ • Python Daemon  │
│ • Avto-apdeyt   │   yig'ish       │ • Kunlik digest  │ • Sharingan Ko'z │
│ • Versiyalar    │ • JSONB format  │ • Model Router   │ • Lokal RVC Ovoz │
│   boshqaruvi   │ • Xatolar mon.  │   Flash vs Pro   │ • Ekran Vision   │
└─────────────────┴─────────────────┴──────────────────┴──────────────────┘
```

---

## 3. Global Arxitektura

```
═══════════════════════════════════════════════════════
              FOYDALANUVCHI QURILMALARI (LOCAL)
═══════════════════════════════════════════════════════

┌───────────────────────────────────────────────────────┐
│     SatoriApps / ItachiAsist (Desktop)               │
│                                                       │
│  ┌──────────────────┐ stdin/stdout ┌───────────────┐ │
│  │  itachi_ui (C#)  │◄────────────►│ itachi_core   │ │
│  │  SkiaSharp 60FPS │  JSON NDJSON │ (Python Master│ │
│  │  Sharingan Eye   │              │ EventBus      │ │
│  │  Neon Pulse      │              │ Screen Vision │ │
│  │  Shaffof Overlay │              │ Edge-TTS+RVC  │ │
│  └──────────────────┘              └───────┬───────┘ │
│  [DayPlan] [OS Watcher] [LanSwitch]────────┘         │
└──────────────────────────────────────┬────────────────┘
                                       │ HTTPS/WebSocket
═══════════════════════════════════════╪════════════════
              SATORI CORE & BACKEND    │
═══════════════════════════════════════╪════════════════
                                       ▼
┌───────────────────────────────────────────────────────┐
│     FastAPI Gateway & Orchestrator (Phase 3)         │
│                                                       │
│  [App Store API]  [Telemetry API]  [AI Agent API]    │
│                                                       │
│  [PostgreSQL+pgvector]  [Redis]  [Celery Workers]    │
└───────────────────────────────────────────────────────┘

  ↕ MAVJUD (SatoriBackend — ASP.NET Core)
┌───────────────────────────────────────────────────────┐
│  Auth API  │  User API  │  PostgreSQL+pgvector        │
│  JWT+BCrypt│  EF Core   │  10 Domain Entity           │
└───────────────────────────────────────────────────────┘
```

---

## 4. Hozirgi Holat (Current State)

### ✅ Tayyor

#### `SatoriBackend` (ASP.NET Core — .NET 10)

| Komponent | Holat |
|-----------|-------|
| 10 ta Domain Entity (`User`, `Family`, `Device`, `LogData`, `InsightData`...) | ✅ To'liq |
| `AuthService` — Login + Register | ✅ |
| `JwtProvider` — Token generatsiya | ✅ |
| `PasswordHasher` — BCrypt | ✅ |
| `UserRepository` — CRUD | ✅ |
| `AppDbContext` — pgvector(768d) + JSONB | ✅ |
| `LoginController` — HttpOnly Cookie | ✅ |
| `RegisterController` | ✅ |
| `JwtMiddleware` + `ExceptionHandlingMiddleware` | ✅ |
| Docker Compose | ✅ |
| Scalar API Docs | ✅ |

#### `SatoriApps/Main/SatoriDesktop` (Avalonia UI)

| Komponent | Holat |
|-----------|-------|
| `LoginWindow.axaml` — Dizayn tayyor | ✅ |
| `MainWindow.axaml` — Log viewer UI | ✅ |
| `MainWindowViewModel.cs` — Mock data | ✅ (real API yo'q) |
| `UserProfile`, `LogEntry` modellar | ✅ |
| `Services/` papkasi | ❌ Bo'sh |

### ❌ Hali Yozilmagan

```
SatoriApps/ItachiAsist/desktop/itachi_core/  ← Bo'sh!
SatoriApps/ItachiAsist/desktop/itachi_ui/   ← Bo'sh!
SatoriApps/ItachiAsist/backend/             ← Bo'sh!
SatoriApps/Main/SatoriDesktop/Services/     ← Bo'sh!
```

---

## 5. Database Schema

### Mavjud (EF Core migrations)
```
Users, Devices, Families, FamilyMembers,
Permissions, MemberPermissions,
LogDatas (pgvector 768d + JSONB),
InsightDatas (pgvector + JSONB),
Sources, Activities
```

### Kerakli qo'shimchalar (Phase 3)

```sql
-- 1. Satori App Store reyestri
CREATE TABLE satori_apps (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug        VARCHAR(100) UNIQUE NOT NULL,
    name        VARCHAR(150) NOT NULL,
    version     VARCHAR(30) NOT NULL,
    manifest    JSONB NOT NULL,
    is_active   BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Markazlashgan faoliyat loglari
CREATE TABLE satori_activity_logs (
    id          BIGSERIAL PRIMARY KEY,
    app_id      UUID REFERENCES satori_apps(id),
    session_id  UUID NOT NULL,
    log_level   VARCHAR(20) NOT NULL,
    category    VARCHAR(50) NOT NULL,
    payload     JSONB NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_logs_payload    ON satori_activity_logs USING GIN (payload);
CREATE INDEX idx_logs_created_at ON satori_activity_logs (created_at DESC);

-- 3. AI kontekstual xotira
CREATE TABLE satori_ai_memories (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    memory_type     VARCHAR(50) NOT NULL,
    summary_text    TEXT NOT NULL,
    embedding       VECTOR(768),
    source_log_ids  BIGINT[],
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 6. Protokollar

### 6.1 itachi_core (Python) ↔ itachi_ui (C#) — stdin/stdout NDJSON

**Python → C# (stdin buyruqlar):**
```json
{"cmd": "WINDOW", "action": "SHOW", "position": "TOP_RIGHT"}
{"cmd": "EYE_STATE", "mode": "IDLE_3TOMOE", "spin_speed": 1.0, "glow": "#AAFF0000"}
{"cmd": "EYE_STATE", "mode": "MANGEKYOU", "spin_speed": 6.5, "glow": "#FFFF0000"}
{"cmd": "AUDIO_AMP", "value": 0.78}
{"cmd": "CHAT_REPLY", "text": "42-qatorda xato bor.", "typing_effect": true}
```

**C# → Python (stdout hodisalar):**
```json
{"event": "UI_READY", "timestamp": 1758900000}
{"event": "USER_TEXT_SUBMIT", "text": "Ekranga qara", "include_screen": true}
{"event": "MIC_BUTTON_TOGGLED", "listening": true}
{"event": "EYE_CLICKED", "button": "RIGHT"}
```

### 6.2 itachi_core → Backend REST API

**Log yuborish:**
```json
POST /api/v1/telemetry/ingest
{
  "app_slug": "itachi-assist",
  "session_id": "uuid",
  "logs": [{"log_level": "INFO", "category": "OS_WINDOW",
             "payload": {"active_app": "code", "duration_sec": 320}}]
}
```

**AI so'rovi:**
```json
POST /api/v1/agent/ask
{
  "prompt": "Nega C# buyruqni olmayapti?",
  "include_recent_logs": true,
  "log_window_minutes": 30,
  "screen_context": {"ocr_text": "JsonException: ..."},
  "persona": "itachi"
}
```

### 6.3 App Manifest (satori_app.json)
```json
{
  "app_id": "uz.satori.itachi_assist",
  "name": "ItachiAssist AI",
  "version": "1.0.0",
  "entry_point": {"linux": "python3 desktop/itachi_core/main.py"},
  "permissions": ["screen_capture", "microphone", "satori_logs_read"],
  "telemetry_stream": "realtime"
}
```

---

## 7. Xavfsizlik

| Tamoyil | Amalga oshirish |
|---------|----------------|
| **PII Scrubber** | API kalitlar, parollar → `[REDACTED]` (lokal RegEx) |
| **Local-First** | TTS, STT, OCR — 100% lokal. Bulutga faqat tozalangan matn |
| **On-Demand Vision** | Ekran faqat buyruqda screenshot, tahlildan so'ng o'chiriladi |
| **JWT + HttpOnly Cookie** | Backend allaqachon tayyor |
| **Scoped Permissions** | Manifest da faqat kerakli ruxsatlar |

---

## 8. 📋 IMPLEMENTATION TASK LIST

---

### PHASE 1: Foundation & Hybrid Bridge
> **Maqsad:** Python itachi_core va C# itachi_ui o'rtasidagi ishchi ko'prik.
> **Holat:** 🔴 Boshlanmagan

#### 📁 Papka Strukturasi

- [ ] **TASK-1.1** — `SatoriApps/ItachiAsist/` to'liq papka strukturasini yaratish:
  ```
  SatoriApps/ItachiAsist/
  ├── satori_app.json
  ├── desktop/
  │   ├── itachi_core/
  │   │   ├── main.py
  │   │   ├── event_bus.py
  │   │   ├── ui_bridge.py
  │   │   ├── plugins/
  │   │   │   ├── __init__.py
  │   │   │   ├── voice_rvc.py
  │   │   │   └── screen_vision.py
  │   │   └── requirements.txt
  │   └── itachi_ui/
  │       ├── ItachiUI.csproj
  │       ├── App.axaml
  │       ├── MainWindow.axaml
  │       ├── MainWindow.axaml.cs
  │       ├── PipeListener.cs
  │       └── SharinganControl.axaml
  └── backend/
      └── app/
          ├── main.py
          ├── routers/
          └── services/
  ```

#### 🐍 itachi_core (Python Master)

- [ ] **TASK-1.2** — `main.py` — Entry point:
  - C# Avalonia ni `subprocess.Popen` orqali ishga tushirish
  - `ui_bridge.py` ni ishga tushirish
  - `event_bus` ni initsializatsiya
  - Graceful shutdown (SIGINT/SIGTERM)

- [ ] **TASK-1.3** — `event_bus.py` — Asinxron hodisalar avtobusi:
  - `subscribe(event_name, callback)` metodi
  - `publish(event_name, data)` metodi
  - `asyncio` asosida, thread-safe
  - Hodisalar: `UI_READY`, `USER_TEXT_SUBMIT`, `MIC_TOGGLED`

- [ ] **TASK-1.4** — `ui_bridge.py` — stdin/stdout protokoli:
  - `send_command(cmd: dict)` → C# ga JSON + `\n`
  - `read_events_loop()` → C# stdout dan asinxron o'qish
  - Kelgan hodisalar → `event_bus.publish()`
  - Xato holatlarda reconnect

- [ ] **TASK-1.5** — `requirements.txt`:
  ```
  edge-tts>=6.1.9
  mss>=9.0.1
  pytesseract>=0.3.10
  Pillow>=10.0.0
  httpx>=0.27.0
  python-dotenv>=1.0.0
  ```

#### 🎨 itachi_ui (C# Avalonia Puppet)

- [ ] **TASK-1.6** — `ItachiUI.csproj` yaratish:
  - .NET 10 target
  - Avalonia UI 11.x
  - SkiaSharp paket

- [ ] **TASK-1.7** — `PipeListener.cs` — stdin JSON o'qish:
  - `StandardInput` stream ni asinxron o'qish
  - `System.Text.Json` bilan parse
  - `cmd` ga qarab: `OnWindowCmd`, `OnEyeStateCmd`, `OnAudioAmpCmd`, `OnChatReplyCmd`

- [ ] **TASK-1.8** — `SharinganControl.axaml` — Sharingan komponenti:
  - Shaffof fon
  - Markaziy qizil doira
  - 3 ta Tomoe (120° da) — aylanish animatsiyasi
  - Neon qizil `DropShadow` effekti
  - **MANGEKYOU mode** — boshqa pattern

- [ ] **TASK-1.9** — `MainWindow.axaml` — Shaffof Overlay:
  - `Background="Transparent"`
  - `Topmost="True"` — har doim ustida
  - O'ng pastki burchakda `SharinganControl`
  - Chat bubble panel (oxirgi javob)
  - Minimal input box + mic tugmasi

- [ ] **TASK-1.10** — `MainWindow.axaml.cs` — Kod orqasidagi mantiq:
  - `PipeListener` ni thread da ishga tushirish
  - `OnEyeStateReceived` → Sharingan mode yangilash
  - `OnAudioAmpReceived` → BoxShadow animatsiya
  - `OnChatReplyReceived` → Typing effect bilan matn
  - Stdout ga: `UI_READY`, `USER_TEXT_SUBMIT`

- [ ] **TASK-1.11** — **Integratsiya testi (MILESTONE 1):**
  - `python main.py` → C# avtomatik ochilsin ✅
  - C# `UI_READY` yuborsin → Python konsolda ko'rinsin ✅
  - Python `EYE_STATE MANGEKYOU` yuborsin → Ko'z o'zgarsin ✅

---

### PHASE 2: Senses — Ovoz va Ko'z
> **Maqsad:** ItachiAsist ni eshita oluvchi va ko'ra oluvchi qilish.
> **Bog'liqlik:** Phase 1 ✅
> **Holat:** 🔴 Boshlanmagan

#### 🎤 Ovoz Tizimi (voice_rvc.py)

- [ ] **TASK-2.1** — Edge-TTS integratsiyasi:
  - `uz-UZ-SardorNeural` ovozi, `rate="-12%"`, `pitch="-5Hz"`
  - Natija `io.BytesIO` buferiga (diskka emas)

- [ ] **TASK-2.2** — Lokal RVC v2 integratsiyasi:
  - `itachi.pth` model (o'zbek talaffuz + Itachi tembri)
  - Edge-TTS audio → RVC orqali o'tkazish

- [ ] **TASK-2.3** — Real-vaqt amplituda uzatish:
  - Har **50ms** da RMS (0.0→1.0) hisoblash
  - `send_command({"cmd": "AUDIO_AMP", "value": rms})`
  - C# → BoxShadow radius animatsiya

- [ ] **TASK-2.4** — EventBus ulash:
  - `event_bus.subscribe("CHAT_REPLY", voice_plugin.speak)`
  - MANGEKYOU → gapiradi → IDLE ketma-ketligi

#### 👁️ Ko'rish Tizimi (screen_vision.py)

- [ ] **TASK-2.5** — `mss` bilan tezkor screenshot:
  - `io.BytesIO` da PIL Image (diskka emas)

- [ ] **TASK-2.6** — `pytesseract` bilan OCR:
  - `image_to_string(img, lang='eng+uzb')`
  - Natija → `screen_context.ocr_text`

- [ ] **TASK-2.7** — On-Demand trigger:
  - `event_bus.subscribe("USER_TEXT_SUBMIT", vision_plugin.capture_if_needed)`
  - Faqat `include_screen: true` da ishlaydi

- [ ] **TASK-2.8** — **Integratsiya testi (MILESTONE 2):**
  - "Ekranga qara" → screenshot + OCR → LLM kontekstga qo'shilsin ✅
  - Itachi gapirsa → neon pulsatsiya ko'rinsin ✅

---

### PHASE 3: Satori Core Integration
> **Maqsad:** Backend bilan to'liq integratsiya — loglar, RAG, AI routing.
> **Bog'liqlik:** Phase 1-2 ✅
> **Holat:** 🔴 Boshlanmagan

#### ⚙️ ItachiAsist Backend (FastAPI)

- [ ] **TASK-3.1** — FastAPI loyiha strukturasini yaratish (yuqorida ko'rsatilgan)

- [ ] **TASK-3.2** — `POST /api/v1/telemetry/ingest` endpointi:
  - Batch loglarni qabul qilish
  - `pii_scrubber.py` tozalash
  - `satori_activity_logs` ga JSONB formatda yozish

- [ ] **TASK-3.3** — `POST /api/v1/agent/ask` endpointi:
  - Boyitilgan prompt yig'ish (loglar + RAG + ekran)
  - `llm_router.py` orqali modelga yuborish

- [ ] **TASK-3.4** — `llm_router.py` — Smart Model Router:
  ```
  Level 1 (Flash-Lite): < 150 belgi, kod yo'q → ~0.3s
  Level 2 (Pro/Opus): "arxitektura", "tahlil", ekran konteksti
  ```

- [ ] **TASK-3.5** — `pii_scrubber.py`:
  - RegEx: `sk-*`, `AIza*`, `.env` qiymatlar, bank kartalar
  - Barcha match → `[REDACTED_SECRET]`

- [ ] **TASK-3.6** — Celery Log Summarizer:
  - Har kuni 23:00 da ishga tushadi
  - 10,000 log → 500 sessiya → 10 ta kunlik xulosa → pgvector

- [ ] **TASK-3.7** — `api_client.py` plagini:
  - `httpx.AsyncClient` bilan backend ga log yuborish
  - Exponential backoff retry

- [ ] **TASK-3.8** — `os_watcher.py` plagini:
  - Linux: `xdotool` orqali faol oyna
  - Har 30s da faol oyna logini backend ga yuborish

- [ ] **TASK-3.9** — itachi_core → Backend integratsiyasi:
  - Foydalanuvchi so'rovi → backend → javob → ovoz

#### 🗃️ SatoriBackend — Yangi migratsiyalar

- [ ] **TASK-3.10** — `satori_activity_logs` EF Core migration + GIN index
- [ ] **TASK-3.11** — `satori_ai_memories` EF Core migration + pgvector(768)

#### 🖥️ SatoriDesktop — Haqiqiy API integratsiya

- [ ] **TASK-3.12** — `Services/ApiService.cs` yaratish:
  - Login/Register haqiqiy backend ga ulash
  - MainWindow da real loglarni API dan olish

- [ ] **TASK-3.13** — **Integratsiya testi (MILESTONE 3):**
  - ItachiAsist ga savol berish → AI kontekst bilan javob qaytarsin ✅
  - OS loglari real-vaqtda backend ga yozilsin ✅

---

### PHASE 4: Ecosystem Expansion
> **Maqsad:** App Store, boshqa ilovalar va Android klient.
> **Bog'liqlik:** Phase 1-3 ✅
> **Holat:** 🔴 Boshlanmagan

- [ ] **TASK-4.1** — `satori_app.json` manifest standartini belgilash
- [ ] **TASK-4.2** — `satori_apps` jadvaliga ilovalarni ro'yxatdan o'tkazish
- [ ] **TASK-4.3** — `GET /api/v1/store/apps` — katalog endpointi
- [ ] **TASK-4.4** — `GET /api/v1/store/apps/{slug}/download` — yuklab olish
- [ ] **TASK-4.5** — Versiya tekshiruvi va avto-yangilanish
- [ ] **TASK-4.6** — Flutter `SatoriApps/Mobile/` loyihasini yaratish
- [ ] **TASK-4.7** — Android "Floating Genjutsu Overlay"
- [ ] **TASK-4.8** — Flutter → Satori Backend auth + AI integratsiya
- [ ] **TASK-4.9** — **DayPlan** → Satori SDK ulash + log yuborish
- [ ] **TASK-4.10** — **OS Watcher** — `systemd` xizmati sifatida
- [ ] **TASK-4.11** — **Cross-App Synergy**: DayPlan + OS Watcher → ItachiAsist eslatma

---

## 9. Roadmap

```
2026 Q4 ──────────────────────────────────────────────────────► 2027 Q1

 PHASE 1         PHASE 2          PHASE 3          PHASE 4
 Foundation      Senses           Core Integr.     Expansion
 ──────────      ────────         ────────────     ─────────
 [Okt 2026]      [Noy 2026]       [Dek 2026]       [2027 Q1]

 • Papka str.    • Edge-TTS       • FastAPI bknd   • App Store
 • itachi_core   • RVC Itachi     • Telemetry API  • Flutter
 • itachi_ui     • Neon pulse     • LLM Router     • DayPlan
 • IPC bridge    • mss OCR        • RAG Memory     • OS Watcher
 • Sharingan     • On-demand      • Celery Sum.    • Cross-app
   3-Tomoe         vision           worker           synergy

 🎯 Milestone:   🎯 Milestone:    🎯 Milestone:    🎯 Milestone:
 Ko'prik ishlaydi Itachi gapiradi AI javob beradi  Ekotizim to'liq
```

---

## 📌 KEYINGI QADAM

> **Hozirgi bosqich:** Phase 1 — Foundation & Hybrid Bridge
>
> **Birinchi taskslar:**
> 1. `TASK-1.1` — Papka strukturasini yaratish
> 2. `TASK-1.2` → `TASK-1.5` — `itachi_core` Python modullari
> 3. `TASK-1.6` → `TASK-1.10` — `itachi_ui` C# Avalonia loyihasi
> 4. `TASK-1.11` — Ko'prik ishlashini tekshirish

---

*Hujjat: 2026-09-26 | Satori Ecosystem v1.0*
