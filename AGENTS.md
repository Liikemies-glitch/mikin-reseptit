# AGENTS.md — Mikin Reseptikirja

Käytä tätä, kun käyttäjä pyytää reseptisuosituksia tai valmistusohjeita Mikin reseptikirjasta.

## Lähteet (hae nämä — ei etusivun HTML:ää)

| Tiedosto | URL | Käyttö |
|---|---|---|
| Markdown | https://liikemies-glitch.github.io/mikin-reseptit/reseptikirja.md | täydet ohjeet |
| JSON | https://liikemies-glitch.github.io/mikin-reseptit/recipes.json | suodatus / haku |
| Indeksi | https://liikemies-glitch.github.io/mikin-reseptit/llms.txt | mitä lukea |

**Älä scrapea** `https://liikemies-glitch.github.io/mikin-reseptit/` HTML-kuorta. Se on JS-SPA eikä sisällä reseptejä ennen kuin `recipes.json` on ladattu selaimessa. Staattiset `.md` / `.json` / `llms.txt` sisältävät kaiken.

## Säännöt

1. **Lue data verkosta** yllä olevista URL-osoitteista. Älä luota muistiin.
2. **Suosittele** 1–3 reseptiä kerrallaan käyttäjän rajoitteiden mukaan (proteiini, kalorit, ainesosat, aika, gluteeniton jne.).
3. **Arvosana** (`rating`, 0–10) kertoo Mikin suosituksen; suosi korkeampia jos käyttäjä ei toisin pyydä. WIP-reseptit (esim. meta sisältää `WIP`) eivät ole valmiita.
4. **Valmistusohjeet** ota vain lähteen `Valmistus`-osiosta. Jos ohje puuttuu, sano se suoraan.
5. **Makrot** ovat arvioita — kerro se lyhyesti.
6. **Kieli:** vastaa käyttäjän kielellä (yleensä suomi).
7. **Linkitä** tarvittaessa UI-reseptiin: `https://liikemies-glitch.github.io/mikin-reseptit/?r=<id>` (id löytyy JSONista, esim. `paaruuat-0`).

## JSON-rakenne (tiivis)

- `sections[].name` — kategoria (Pääruoat, Jälkiruoat, Kastikkeet ja soosit)
- `sections[].recipes[].title` — reseptin nimi
- `sections[].recipes[].meta` — annoskoko / WIP-merkintä ym.
- `sections[].recipes[].rating` — arvosana 0–10
- `sections[].recipes[].id` — URL-id (`?r=`)
- `sections[].recipes[].blocks[]` — osiot: `Ainekset`, `Valmistus`, `Makrot`, `Huom`, `Vinkki`, …
- `index[]` — litteä lista UI:ta varten (title, meta, macros, rating, section)

## Esimerkkiprompti käyttäjälle

> Käytä lähteenä https://liikemies-glitch.github.io/mikin-reseptit/llms.txt  
> Hae reseptikirja.md tai recipes.json. Suosittele illallista ~40 g proteiinilla ja anna valmistusohjeet.
