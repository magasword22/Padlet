# Padlet CEJM – texte extrait par OCR

Texte extrait du document « Padlet CEJM » (PDF de 505 pages, composé uniquement d'images).

| Fichier | Contenu |
|---|---|
| `padlet_cejm_propre.txt` | Texte nettoyé, avec un repère `===== Page N =====` au début de chaque page. **C'est la version à utiliser.** |
| `padlet_cejm_ocr.txt` | Sortie brute de l'OCR, sans correction (pages séparées par un saut de page). |
| `scripts/nettoyage_ocr.py` | Script qui produit la version nettoyée à partir de la sortie brute. |

## Méthode

1. OCR avec OCRmyPDF et Tesseract (français + anglais).
2. Nettoyage automatique :
   - « La / Les / Le » mis en minuscule au milieu des phrases ;
   - apostrophe lue comme un « V » (« Vemployeur » → « l’employeur ») ;
   - « ILpeut » → « Il peut » ;
   - accents mal reconnus (« prés » → « près », « étre » → « être »…) ;
   - suppression des lignes parasites issues des images.

Relancer le nettoyage (nécessite la liste de mots `wfrench`, `/usr/share/dict/french`) :

```
python3 scripts/nettoyage_ocr.py padlet_cejm_ocr.txt padlet_cejm_propre.txt lignes_supprimees.txt
```

## Limites connues

- Quand le texte d'une image se trouve sur la même ligne qu'une phrase du cours, le fragment parasite est conservé.
- Quelques erreurs isolées subsistent (ex. « a » au lieu de « à »).
- Le PDF avec texte sélectionnable (171 Mo) n'est pas dans ce dépôt : il dépasse la limite de 100 Mo par fichier de GitHub.
