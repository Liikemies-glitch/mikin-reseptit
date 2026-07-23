# Ateriakuvat

Laita reseptikuvat tähän kansioon. Build (`python3 build_recipes.py`) liittää ne automaattisesti.

## Nimeäminen

Tiedostonimi kertoo reseptin. Esimerkkejä:

| Tiedosto | Resepti |
|---|---|
| `rahkapohja-pizza.jpg` | Rahkapohja-pizza |
| `rahkapohja-pizza-2.jpg` | sama, toinen kuva |
| `pizza.jpg` / `joku-piz.jpg` | Rahkapohja-pizza (alias) |
| `kanatortillat.jpg` | Kanatortillat |
| `rullakebab.jpg` / `kebab.jpg` | Rullakebab |
| `kreikkalainen-moussaka.jpg` / `moussaka.jpg` | Kreikkalainen moussaka |
| `keltainen-curry.jpg` / `curry.jpg` | Keltainen curry |
| `mausteinen-jauhelihapata.jpg` | Mausteinen jauhelihapata |
| `intialainen-jauhelihakeema.jpg` / `keema.jpg` | Intialainen jauhelihakeema |
| `proteiini-porkkanakakku.jpg` | Proteiini-porkkanakakku |

Tai kansio: `images/rahkapohja-pizza/uuni.jpg`

## Vaihtoehdot

1. **manifest.json** — `{ "rahkapohja-pizza": ["oma-nimi.jpg"] }`
2. Markdownissa: `**Kuvat:** rahkapohja-pizza.jpg, rahkapohja-pizza-2.jpg`

Tuettu: `.jpg` `.jpeg` `.png` `.webp` `.gif`
