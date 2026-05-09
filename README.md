# Satori Project

Satori — bu foydalanuvchilar, oila a'zolari va qurilmalar faolligini kuzatish, ma'lumotlarni tahlil qilish (insight) va boshqarish uchun mo'ljallangan zamonaviy tizimdir. Loyiha Clean Architecture (Toza arxitektura) prinsiplari asosida ishlab chiqilgan **ASP.NET Core Backend** va kross-platforma qo'llab-quvvatlovchi **Avalonia UI Desktop** ilovasidan iborat.

## 🛠 Texnologiyalar Steki

### Backend (`SatoriBackend`)
*   **Freymvork:** .NET 10, ASP.NET Core Web API
*   **Arxitektura:** Clean Architecture (Domain, Application, Infrastructure, API)
*   **Ma'lumotlar bazasi:** PostgreSQL
*   **ORM:** Entity Framework Core
*   **Qo'shimcha:** `pgvector` (Vektor qidiruv va AI tahlillari uchun qo'llab-quvvatlash)
*   **Xavfsizlik:** JWT Autentifikatsiya, BCrypt Parol heshlash
*   **Infratuzilma:** Docker, Docker Compose

### Mijoz Ilovasi (`SatoriApps/Main/SatoriDesktop`)
*   **Freymvork:** .NET 10, Avalonia UI
*   **Arxitektura:** MVVM (Model-View-ViewModel)
*   **Dizayn:** Fluent Themes

---

## 📂 Loyiha Tuzilishi

Loyiha ikkita asosiy qismga bo'lingan:

### 1. SatoriApps (Desktop Mijoz)
Avalonia UI freymvorkida yozilgan foydalanuvchi interfeysi.
*   `Views/` - Foydalanuvchi interfeysi oynalari (`MainWindow.axaml`, `LoginWindow.axaml`).
*   `ViewModels/` - UI mantiqi va ma'lumotlarni bog'lash (Data Binding).
*   `Models/` - Mijoz tomonidagi ma'lumotlar tuzilmasi (`UserProfile`, `LogEntry`).
*   `Services/` & `Helpers/` - API bilan ishlash va yordamchi funksiyalar.

### 2. SatoriBackend (API Server)
Clean Architecture asosida qurilgan API server.
*   **`Satori.Api`**: Kirish nuqtasi. JWT Middlewares, Exception Handling va Kontrollerlar (`AuthController`, `UserController`).
*   **`Satori.Application`**: Biznes mantiq. DTOlar (`LoginRequest`, `RegisterRequest`), interfeyslar, maxsus xatolar (Exceptions) va xizmatlar (`AuthService`).
*   **`Satori.Domain`**: Asosiy ma'lumotlar modellari va entitilar (`User`, `Family`, `Device`, `InsightData`, `LogData`, `Activity`, `Permission`).
*   **`Satori.Infrastructure`**: EF Core orqali ma'lumotlar bazasi bilan ishlash (`AppDbContext`, `UserRepository`), Migratsiyalar hamda `JwtProvider` kabi tashqi xizmatlar realizatsiyasi.

---

## ✨ Asosiy Imkoniyatlar

*   **Autentifikatsiya va Avtorizatsiya:** JWT asosida xavfsiz tizimga kirish va ro'yxatdan o'tish.
*   **Foydalanuvchi va Oila boshqaruvi:** Oila a'zolarini va ularning ruxsatlarini (Permissions) boshqarish.
*   **Qurilmalar monitoringi:** Qurilmalar va faollik (Activity) tarixini yozib borish.
*   **Tahlil va Loglar:** `LogData` va `InsightData` orqali tizim va foydalanuvchi faoliyatini aqlli tahlil qilish (pgvector integratsiyasi bilan).

---

## 🚀 O'rnatish va Ishga tushirish

### Talablar
*   [.NET 10 SDK](https://dotnet.microsoft.com/)
*   [Docker](https://www.docker.com/) (Backend va DB ni oson ishga tushirish uchun)

### Backendni ishga tushirish (Docker orqali)
1. Terminalni oching va `SatoriBackend` papkasiga kiring:
   ```bash
   cd SatoriBackend
   docker compose up --build
