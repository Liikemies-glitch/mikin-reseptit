# Mikin Reseptikirja

Proteiinipainotteinen reseptikirja verkossa.

**Sivusto (ihmisille):** https://liikemies-glitch.github.io/mikin-reseptit/

## Anna agentille tämä URL (ei etusivua)

Etusivu on JavaScript-SPA — ChatGPT/Claude näkee siitä usein vain tyhjän kuoren. Anna agentille sen sijaan:

```text
https://liikemies-glitch.github.io/mikin-reseptit/llms.txt
```

tai suoraan koko kirja:

```text
https://liikemies-glitch.github.io/mikin-reseptit/reseptikirja.md
```

### Esimerkki Cursorille / ChatGPT:lle / Claudelle

> Käytä lähteenä https://liikemies-glitch.github.io/mikin-reseptit/llms.txt  
> Hae sieltä linkatut `reseptikirja.md` tai `recipes.json` (älä scrapea etusivun HTML:ää).  
> Suosittele proteiinipitoista illallista ja anna valmistusohjeet suomeksi.

## Data

| Tiedosto | Sisältö |
|---|---|
| `reseptikirja.md` | Koko kirja Markdownina |
| `recipes.json` | Strukturoitu data |
| `llms.txt` | Agenttien sisällysluettelo |
| `AGENTS.md` | Agentin käyttöohje |

## Paikallinen ajo

```bash
python3 -m http.server 8080
```
