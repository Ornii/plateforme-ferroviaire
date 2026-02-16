Projet de pilotage d’un aiguillage ferroviaire miniature avec :
- un **Arduino** (esclave I2C) qui pilote LEDs, capteurs Hall et servo,
- un **Raspberry Pi** (maître I2C) qui exécute la logique de circulation.
- 
---

## 1) Architecture du projet

```text
railroad_switch/
├── slave-arduino/
│   └── main/main.ino
└── master-raspberry/
    ├── main.py
    ├── communication/
    ├── components/
    ├── train/
    └── ...
```

- `slave-arduino/main/main.ino` : firmware Arduino, adresse I2C `0x08`.
- `master-raspberry/main.py` : point d’entrée Python côté Raspberry.

---

## 2) Prérequis matériel

- 1 Raspberry Pi (I2C activé)
- 1 Arduino
- Liaison I2C entre Raspberry et Arduino
- Capteurs Hall + LEDs (rouge/verte) + servo d’aiguillage
- Alimentation adaptée

---

## 3) Prérequis logiciel

### Arduino
- Arduino IDE (ou CLI Arduino)
- Bibliothèques utilisées par le firmware :
  - `Wire`
  - `Servo`

### Raspberry
- Python 3.10+ recommandé
- Dépendance Python :
  - `smbus2`

Installation recommandée :

```bash
cd railroad_switch/master-raspberry
python3 -m venv .venv
source .venv/bin/activate
pip install smbus2
```

---

## 4) Déploiement et exécution

### Étape A — Charger le firmware Arduino

1. Ouvrir `railroad_switch/slave-arduino/main/main.ino`
2. Compiler et téléverser sur l’Arduino
3. Vérifier que l’adresse I2C reste `0x08`

### Étape B — Lancer le programme Raspberry

Depuis le dossier `master-raspberry` :

```bash
cd railroad_switch/master-raspberry
python3 main.py
```

> Important : le code utilise des imports relatifs à ce dossier, donc il faut lancer `main.py` depuis `master-raspberry`.

---

## 5) Comportement attendu

- Le train a une position initiale (`init_position`) et un objectif (`objective_position`) définis dans `main.py`.
- L’initialisation (`init_setup`) :
  - lit l’état de l’aiguillage,
  - met certains feux au rouge,
  - positionne l’aiguillage selon l’objectif.
- La boucle principale attend la détection des capteurs Hall pour confirmer l’arrivée à l’objectif.

---

## 6) Limitations connues

- Le firmware Arduino est conçu avec une logique de capteurs qui nécessite souvent un **reflash avant un nouveau passage** (comportement actuel du projet).
- Le projet n’inclut pas encore de gestion d’erreurs avancée (timeouts I2C, validation complète des scénarios de trajet).
- Ce dépôt contient des améliorations en cours ; vérifier les TODO dans le code pour les prochaines évolutions.

---
