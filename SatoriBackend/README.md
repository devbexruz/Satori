# 🧠 Satori Backend (Core Engine)

Bu **Satori** ekotizimining markaziy qismi bo'lib, barcha loglarni qabul qilish, ularni sun'iy intellekt (Gemini) yordamida vektorizatsiya qilish va semantik tahlil qilish uchun javobgardir.

## 🏗 Arxitektura
Backend **Clean Architecture** tamoyillari asosida qurilgan bo'lib, quyidagi qatlamlardan iborat:

*   **Satori.Api:** Tashqi dunyo bilan aloqa (REST API). Mikroservislar va mijozlar shu qatlam orqali log yuboradi.
*   **Satori.Application:** Biznes mantiq va use-case'lar (masalan: logni qayta ishlash oqimi).
*   **Satori.Domain:** Tizimning "yuragi" — entitilar, qiymat ob'ektlari va biznes qoidalari.
*   **Satori.Infrastructure:** Tashqi xizmatlar bilan integratsiya (PostgreSQL, Gemini API, Redis va h.k.).

## 🛠 Texnologiyalar
*   **Platforma:** .NET 8/9
*   **Ma'lumotlar ombori:** PostgreSQL + **pgvector** (Vektorli qidiruv uchun).
*   **AI Integratsiya:** Gemini `text-embedding-004` (Embedding generation).
*   **ORM:** Entity Framework Core.
*   **Konteynerizatsiya:** Docker (kelajakda mikroservislar bilan ishlash uchun).

## 🚀 Funksional imkoniyatlar
1.  **Log Ingestion:** Turli manbalardan kelgan xom loglarni qabul qilish.
2.  **Semantic Vectorization:** Har bir log matnini Gemini yordamida 768 o'lchamli vektorga aylantirish.
3.  **Vector Persistence:** Matn va vektorni optimal ko'rinishda bazaga saqlash.
4.  **Insight Generation (Background):** Fondagi vazifalar orqali loglar orasidagi bog'liqliklarni topish.

## ⚙️ Sozlamalar (Setup)
Loyiha ishlashi uchun `.env` faylida quyidagi kalitlar bo'lishi shart:

```env
ConnectionStrings__DefaultConnection="Host=localhost;Database=satori_db;Username=postgres;Password=your_password"
Gemini__ApiKey="YOUR_GEMINI_API_KEY_HERE"
Gemini__Model="text-embedding-004"
```

## 📂 Loyiha tuzilishi
```text
Satori/
├── SatoriBackend/                 # Markaziy API va Mantiq
│   ├── Satori.Api/
│   ├── Satori.Application/
│   ├── Satori.Domain/
│   ├── Satori.Infrastructure/
│   ├── Microservices/           # Kelajakdagi boshqa xizmatlar (TBA)
│   │   ├── Satori.TelegramBot/
│   │   ├── Satori.Scraper/
│   │   └── ...
│   └── docker-compose.yml
└── SatoriApps/
    ├── Manga
    ├── DayPlan
    └── ...
```

## 🛠 Ishga tushirish
```bash
cd Backend
dotnet restore
dotnet build
dotnet run --project Satori.Api
```

---

### 📝 Eslatma
Backend faqat "ma'lumotlarni qayta ishlash" (data processing) bilan shug'ullanadi. Unda interaktiv chat mavjud emas. Ma'lumotlarni olish va qidirish uchun API endpoint'lardan foydalaniladi.

---

**Satori Backend — Logic, Data, and Enlightenment.**