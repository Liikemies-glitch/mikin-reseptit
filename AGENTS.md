# AGENTS.md — Mikin Reseptikirja

Käytä tätä, kun käyttäjä pyytää reseptisuosituksia tai valmistusohjeita Mikin reseptikirjasta.

## Lähteet (hae nämä)

| Tiedosto | URL | Käyttö |
|---|---|---|
| Markdown | https://liikemies-glitch.github.io/mikin-reseptit/reseptikirja.md | täydet ohjeet |
| JSON | https://liikemies-glitch.github.io/mikin-reseptit/recipes.json | suodatus / haku |
| Indeksi | https://liikemies-glitch.github.io/mikin-reseptit/llms.txt | mitä lukea |

## Säännöt

1. **Lue data verkosta** yllä olevista URL-osoitteista. Älä luota muistiin.
2. **Suosittele** 1–3 reseptiä kerrallaan käyttäjän rajoitteiden mukaan (proteiini, kalorit, ainesosat, aika, gluteeniton jne.).
3. **Valmistusohjeet** ota vain lähteen `Valmistus`-osiosta. Jos ohje puuttuu, sano se suoraan.
4. **Makrot** ovat arvioita — kerro se lyhyesti.
5. **Kieli:** vastaa käyttäjän kielellä (yleensä suomi).
6. **Linkitä** tarvittaessa UI-reseptiin: `https://liikemies-glitch.github.io/mikin-reseptit/?r=<id>` (id löytyy JSONista, esim. `paaruuat-0`).

## JSON-rakenne (tiivis)

- `sections[].name` — kategoria (Pääruoat, Pizzat, …)
- `sections[].recipes[].title` — reseptin nimi
- `sections[].recipes[].meta` — annoskoko / kesto
- `sections[].recipes[].id` — URL-id (`?r=`)
- `sections[].recipes[].blocks[]` — osiot: `Ainekset`, `Valmistus`, `Makrot`, …

## Esimerkkiprompti käyttäjälle

> Käytä lähteenä https://liikemies-glitch.github.io/mikin-reseptit/llms.txt  
> Suosittele illallista ~40 g proteiinilla ja anna valmistusohjeet.
