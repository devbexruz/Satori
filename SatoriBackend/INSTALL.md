**1. Paketni o'rnatish:**
Postgres versiyangiz 18 (yoki 16/17) ekanligini hisobga olib, eng ishonchli yo'li — server-dev paketlari orqali o'rnatish:
```bash
sudo apt update
sudo apt install postgresql-server-dev-all gcc make
```

**2. pgvector-ni manba kodidan (source) o'rnatish:**
Agar `apt install postgresql-16-pgvector` kabi tayyor paket topilmasa (ba'zan Debian repozitoriyalarida kechikadi), bu eng aniq yo'li:
```bash
cd /tmp
git clone --branch v0.7.0 https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install # Parolingizni so'raydi
```

**3. Postgres-ni restart qilish:**
Yangi o'rnatilgan modulni Postgres ko'rishi uchun uni qayta yoqish shart:
```bash
sudo systemctl restart postgresql
```

### Endi migratsiyani qayta ishga tushiring

Endi yana `Satori.Api` papkasiga qaytib, bazani yangilang:
```bash
dotnet ef database update --project ../Satori.Infrastructure --startup-project .
```

---

### Agar hali ham bo'lmasa (Muqobil yo'l):
Agar Linux tizimingizga modul o'rnatishda qiynalsangiz, eng oson va zamonaviy yo'l — **Docker** ishlatish. 
`pgvector` allaqachon ichiga o'rnatilgan tayyor Postgres obrazini bir soniyada ko'tarish mumkin:
```bash
docker run --name satori-db -e POSTGRES_PASSWORD=admin1234 -p 5432:5432 -d pgvector/pgvector:pg16
```
Keyin `appsettings.json` dagi parolni `admin1234` qilib qo'ysangiz kifoya.

**Vektor kengaytmasi muvaffaqiyatli o'rnatildimi?** `Done` yozuvini ko'rgan bo'lsangiz, demak g'alaba qozondik! Keyingi qadamda Gemini AI-ni ulaymizmi?