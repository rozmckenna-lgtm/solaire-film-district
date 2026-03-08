# Solaire Film District — Documentation technique

## Table des matieres

1. [Architecture et structure des fichiers](#architecture-et-structure-des-fichiers)
2. [Logique de la structure](#logique-de-la-structure)
3. [Design system](#design-system)
4. [Conventions techniques](#conventions-techniques)
5. [Integration Formspree](#integration-formspree)
6. [Deploiement GitHub Pages](#deploiement-github-pages)
7. [Configuration DNS (OVH)](#configuration-dns-ovh)
8. [Chemin vers un CMS](#chemin-vers-un-cms)
9. [Fonctionnalites de reservation (Booking)](#fonctionnalites-de-reservation-booking)
10. [Maintenance](#maintenance)

---

## Architecture et structure des fichiers

```
/
├── index.html           Landing page / accueil institutionnel
├── vision.html          Vision et mission du district
├── loi.html             Information sur les lettres d'intention
├── loi-form.html        Formulaire LOI (Formspree POST)
├── thank-you.html       Page de confirmation post-soumission
├── css/
│   └── style.css        Feuille de style unique et partagee
├── CNAME                Domaine personnalise GitHub Pages
├── DOCUMENTATION.md     Ce fichier
└── README.md            README du depot
```

## Logique de la structure

### Pourquoi des fichiers HTML a la racine ?

GitHub Pages sert les fichiers statiques depuis la racine du depot. En placant tous les `.html` a la racine, les URL sont directement previsibles :

- `solairefilmdistrict.fr/` → `index.html`
- `solairefilmdistrict.fr/vision.html`
- `solairefilmdistrict.fr/loi.html`
- `solairefilmdistrict.fr/loi-form.html`
- `solairefilmdistrict.fr/thank-you.html`

### Pourquoi une seule feuille de style ?

Avec cinq pages partageant le meme design system, une feuille de style unique simplifie la maintenance, evite les problemes de specificite, et reduit les requetes HTTP. Les custom properties CSS (variables) centralisent les tokens de design.

### Pourquoi pas de JavaScript ?

Le site est institutionnel et informatif. Le formulaire utilise la soumission HTML native vers Formspree. L'absence de JS garantit :

- Performance maximale (pas de bundle a charger)
- Accessibilite native
- Securite (pas de surface d'attaque cote client)
- Maintenabilite (aucune dependance a mettre a jour)

## Design system

### Palette de couleurs

La palette est derivee du logo officiel Solaire Film District : fond sombre avec accents dores.

| Token | Valeur | Usage |
|-------|--------|-------|
| `--color-bg` | `#111114` | Fond principal (noir profond) |
| `--color-bg-alt` | `#1A1A1F` | Fond alternatif (sections) |
| `--color-surface` | `#222228` | Surfaces (cartes, inputs) |
| `--color-text` | `#E8E4DD` | Texte principal (blanc chaud) |
| `--color-text-muted` | `#9B978F` | Texte secondaire |
| `--color-accent` | `#C9A84C` | Accent dore (boutons, liens, accents) |
| `--color-accent-hover` | `#DDB94F` | Accent hover (dore clair) |
| `--color-border` | `#2E2E35` | Bordures subtiles |

### Typographie

Pile de polices systeme : `'Segoe UI', 'Helvetica Neue', Arial, sans-serif`

Echelle typographique en `rem` de 0.75rem a 3rem. Titres en majuscules avec espacement de lettres pour le hero.

### Espacement

Echelle d'espacement de `0.25rem` (xs) a `6rem` (4xl). Approche coherente via custom properties.

### Composants

- **Boutons** : `.btn-primary` (dore plein) et `.btn-outline` (bordure doree)
- **Cartes** : fond surface, bordure subtile, titre en accent
- **Formulaires** : inputs sur fond sombre, focus avec halo dore
- **Hero divider** : trait dore horizontal sous les titres de page

## Conventions techniques

- **Langue** : `lang="fr"` sur toutes les balises `<html>`
- **Encodage** : UTF-8
- **Viewport** : `width=device-width, initial-scale=1.0`
- **Approche responsive** : mobile-first (styles de base = mobile, media queries a 40rem et 64rem)
- **Accessibilite** : skip-nav, aria-current, aria-label sur nav, labels sur tous les champs, hierarchie h1→h2→h3
- **Nommage CSS** : BEM-inspired simplifie (`.site-header`, `.form-group`, `.page-hero`, `.section--alt`)
- **Unites** : `rem` pour la typographie et les espacements, `px` uniquement pour les bordures

## Integration Formspree

- **Endpoint** : `https://formspree.io/f/xwvkjpaz`
- **Methode** : POST (soumission HTML native)
- **Redirection** : champ cache `_next` pointant vers `https://solairefilmdistrict.fr/thank-you.html`
- **Anti-spam** : champ honeypot `_gotcha` cache via CSS
- **Sujet** : champ cache `_subject` avec valeur fixe
- **Reply-to** : Formspree utilise automatiquement le champ `name="email"`

### Champs du formulaire

| Champ | `name` | Type | Requis |
|-------|--------|------|--------|
| Organisation | `organisation` | text | oui |
| Nom du contact | `contact_name` | text | oui |
| E-mail | `email` | email | oui |
| Telephone | `phone` | tel | non |
| Site web | `website_url` | url | non |
| Titre du projet | `project_title` | text | oui |
| Type de projet | `project_type` | select | oui |
| Synopsis | `synopsis` | textarea | oui |
| Intentions artistiques | `artistic_intent` | textarea | non |
| Date de debut | `timeline_start` | date | oui |
| Date de fin | `timeline_end` | date | non |
| Jours de tournage | `shooting_days` | text | non |
| Budget | `budget_range` | select | oui |
| Statut financement | `funding_status` | select | non |
| Lieux de tournage | `location_needs` | textarea | non |
| Ressources locales | `local_resources` | textarea | non |
| Infos complementaires | `additional_info` | textarea | non |
| Source | `referral_source` | select | non |

## Deploiement GitHub Pages

### Etapes

1. Creer un depot GitHub (ou utiliser le depot existant)
2. Pousser tout le code a la racine du depot
3. Aller dans **Settings → Pages**
4. Source : **Deploy from a branch**
5. Branch : `main` / dossier `/ (root)`
6. Sauvegarder
7. Le fichier `CNAME` est automatiquement lu par GitHub Pages
8. GitHub Pages provisionne automatiquement un certificat SSL Let's Encrypt

### Verification

- `https://<username>.github.io/<repo>/` doit fonctionner immediatement
- `https://solairefilmdistrict.fr/` fonctionnera une fois le DNS configure

## Configuration DNS (OVH)

Le domaine `SolaireFilmDistrict.fr` est heberge chez OVH. Pour le pointer vers GitHub Pages :

### Etape 1 : Enregistrements DNS dans l'espace client OVH

Aller dans **Domaines → SolaireFilmDistrict.fr → Zone DNS** et ajouter :

#### Enregistrements A (apex domain)

```
Type : A    Sous-domaine : (vide)    Cible : 185.199.108.153    TTL : 3600
Type : A    Sous-domaine : (vide)    Cible : 185.199.109.153    TTL : 3600
Type : A    Sous-domaine : (vide)    Cible : 185.199.110.153    TTL : 3600
Type : A    Sous-domaine : (vide)    Cible : 185.199.111.153    TTL : 3600
```

#### Enregistrement CNAME (sous-domaine www)

```
Type : CNAME    Sous-domaine : www    Cible : <username>.github.io.    TTL : 3600
```

> Remplacer `<username>` par le nom d'utilisateur ou d'organisation GitHub.

#### Enregistrements AAAA (IPv6)

```
Type : AAAA    Sous-domaine : (vide)    Cible : 2606:50c0:8000::153    TTL : 3600
Type : AAAA    Sous-domaine : (vide)    Cible : 2606:50c0:8001::153    TTL : 3600
Type : AAAA    Sous-domaine : (vide)    Cible : 2606:50c0:8002::153    TTL : 3600
Type : AAAA    Sous-domaine : (vide)    Cible : 2606:50c0:8003::153    TTL : 3600
```

### Etape 2 : Supprimer les enregistrements conflictuels

Supprimer tout enregistrement A, AAAA ou CNAME existant pour le sous-domaine racine qui pointerait vers les serveurs OVH par defaut.

### Etape 3 : Verification

Apres propagation DNS (jusqu'a 48h, generalement 1-4h) :

```bash
dig solairefilmdistrict.fr +short
# Doit retourner les 4 IP GitHub Pages

dig www.solairefilmdistrict.fr +short
# Doit retourner <username>.github.io.
```

### Etape 4 : HTTPS

Dans **GitHub → Settings → Pages**, cocher **Enforce HTTPS** une fois que le certificat SSL est provisionne.

## Chemin vers un CMS

Le site est actuellement en HTML/CSS statique pur. Chemins d'evolution possibles :

### Option 1 : CMS headless leger (Decap CMS)

- Ajout d'un fichier `admin/index.html` et `admin/config.yml`
- Impact tres faible sur l'architecture existante
- Necessite migration vers Netlify ou Cloudflare Pages pour OAuth

### Option 2 : Generateur de sites statiques (Hugo, Eleventy, Jekyll)

- Pages generees a partir de templates et fichiers Markdown
- Restructuration du projet necessaire
- Jekyll est natif a GitHub Pages

### Option 3 : CMS complet (WordPress, Strapi)

- Backend dedie, base de donnees, API REST
- Uniquement si le volume de contenu le justifie

### Recommandation

**Option 2 avec Eleventy** : le HTML existant peut etre converti en templates Nunjucks avec un effort minimal, le CSS reste inchange, compatible GitHub Pages via GitHub Action.

## Fonctionnalites de reservation (Booking)

### Solutions envisageables

| Solution | Complexite | Cout |
|----------|-----------|------|
| Calendly (embed) | Faible | Gratuit/payant |
| Cal.com (self-hosted) | Moyenne | Gratuit |
| Developpement custom (Next.js + Supabase) | Elevee | Hebergement |
| Plugin WordPress (Amelia, BookingPress) | Moyenne | Licence |

### Recommandation

Pour une premiere iteration, **Calendly ou Cal.com en embed** permet d'ajouter un systeme de reservation sans modifier l'architecture actuelle.

## Maintenance

### Mise a jour du contenu

Modifier directement les fichiers HTML. Chaque page est autonome et lisible.

### Mise a jour du design

Toutes les valeurs visuelles sont centralisees dans les custom properties CSS en haut de `css/style.css`. Modifier une couleur ou une taille de police se fait en un seul endroit.

### Ajout d'une page

1. Dupliquer un fichier HTML existant
2. Modifier le contenu dans `<main>`
3. Mettre a jour le `<title>` et la `<meta name="description">`
4. Mettre a jour `aria-current="page"` dans la navigation
5. Ajouter le lien dans la navigation de **tous** les fichiers HTML

### Surveillance

- Verifier regulierement que le certificat SSL est actif
- Tester le formulaire Formspree periodiquement
- Valider l'accessibilite avec WAVE ou axe DevTools
