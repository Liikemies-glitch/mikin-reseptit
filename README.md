# Mikin Reseptikirja

Proteiinipainotteinen reseptikirja verkossa.

**Sivusto:** https://liikemies-glitch.github.io/mikin-reseptit/

## Anna agentille tämä URL

```text
https://liikemies-glitch.github.io/mikin-reseptit/llms.txt
```

Agentti lukee sieltä Markdown/JSON-lähteet, suosittelee reseptejä ja antaa valmistusohjeet. Katso myös [AGENTS.md](./AGENTS.md).

### Esimerkki Cursorille / ChatGPT:lle / Claudelle

> Käytä lähteenä https://liikemies-glitch.github.io/mikin-reseptit/llms.txt  
> Suosittele proteiinipitoista illallista ja anna valmistusohjeet suomeksi.

## Ihmisen UI

Avaa https://liikemies-glitch.github.io/mikin-reseptit/

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
