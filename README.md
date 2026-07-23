# Mikin Reseptikirja

Proteiinipainotteinen reseptikirja verkossa. Visuaalinen kieli: Refero **19–86** (`DESIGN.md`).

## Paikallinen ajo

```bash
python3 -m http.server 8080
```

Avaa http://localhost:8080

## Julkaisu GitHub Pagesiin

```bash
git remote add origin https://github.com/Liikemies-glitch/mikin-reseptit.git
git push -u origin main
```

Sitten GitHubissa: **Settings → Pages → Branch: `main` → folder: `/ (root)` → Save**

Sivusto: `https://liikemies-glitch.github.io/mikin-reseptit/`

## Rakenne

| Tiedosto | Sisältö |
|---|---|
| `index.html` | Hakemisto + reseptinäkymä |
| `styles.css` | 19–86-tokenit |
| `app.js` | Suodatus ja navigointi |
| `recipes.json` | Parsitut reseptit |
| `reseptikirja.md` | Lähdemarkdown |
| `DESIGN.md` | Refero-tyylitiedosto |
