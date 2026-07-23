# Mikin Reseptikirja

Proteiinipainotteinen reseptikirja verkossa. Visuaalinen kieli: Refero **19–86** (`DESIGN.md`).

## Paikallinen ajo

```bash
python3 -m http.server 8080
```

Avaa http://localhost:8080

## Julkaisu GitHub Pagesiin

Repo ei ole vielä olemassa. Luo se ja työnnä koodi:

```bash
# 1) Luo tyhjä repo GitHubissa nimellä mikin-reseptikirja (Liikemies-glitch)
# 2) Tässä kansiossa:
git remote add origin https://github.com/Liikemies-glitch/mikin-reseptikirja.git
git push -u origin main
```

Sitten GitHubissa: **Settings → Pages → Branch: `main` → folder: `/ (root)` → Save**

Sivusto: `https://liikemies-glitch.github.io/mikin-reseptikirja/`

## Rakenne

| Tiedosto | Sisältö |
|---|---|
| `index.html` | Hakemisto + reseptinäkymä |
| `styles.css` | 19–86-tokenit |
| `app.js` | Suodatus ja navigointi |
| `recipes.json` | Parsitut reseptit |
| `reseptikirja.md` | Lähdemarkdown |
| `DESIGN.md` | Refero-tyylitiedosto |
