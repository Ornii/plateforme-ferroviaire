Projet de pilotage d’un aiguillage ferroviaire avec :
- un **Arduino** (esclave I2C) qui pilote LEDs, capteurs Hall et servo,
- un **Raspberry Pi** (maître I2C) qui exécute la logique de circulation.

---

## 1) Architecture du projet

```text
railroad_switch/
├── slave-arduino/
│   └── main/main.ino
└── master-raspberry/
    ├── main.py
    ├── communication/
    │   └── hall_sensors/
    │   │   └── encoding.py
    │   │   └── state.py
    │   │   └── ...
    │   └── blade_switch/
    │   └── ...
    ├── components/
    ├── train/
    └── ...
```

- `slave-arduino/main/main.ino` : firmware Arduino
- `master-raspberry/main.py` : script Python côté Raspberry.

---

## 2) Prérequis matériel

- 1 Raspberry Pi (I2C activé)
- 1 Arduino (addresse I2C `0x08`)
- Liaison I2C entre Raspberry et Arduino
- Capteurs Hall + LEDs (rouge/verte) + servo pour l'aiguillage + aiguillage

---

## 3) Prérequis logiciel

### Arduino
- Arduino IDE
- Bibliothèques utilisées par le firmware :
  - `Wire`
  - `Servo`

Les bilibothèques sont déjà présentent sur l'IDE Arduiuno.

### Raspberry
- Python 3.10+
- Dépendance Python :
  - `smbus2`

Installation :

```bash
pip install smbus2
```

---

## 4) Déploiement et exécution

### Étape A — Charger le firmware Arduino

1. Ouvrir `railroad_switch/slave-arduino/main/main.ino`
2. Compiler et téléverser sur l’Arduino

### Étape B — Lancer le programme Raspberry

Depuis le dossier `master-raspberry` :

```bash
cd railroad_switch/master-raspberry
python3 main.py
```

> Important : le code utilise des imports relatifs à ce dossier, donc il faut lancer `main.py` depuis `master-raspberry`.

---

## 5) Utilisation

- Le train a une position initiale (`init_position`) et un objectif (`objective_position`) définis dans `main.py`.
Ces deux valeurs peuvent être changés, tant qu'elles sont possibles pour un train dans `main.py`.
- Il est possible de changer l'adresse I2C de l'Arduino dans `main.py`. 

---

## 6) Limitations connues

- Le firmware Arduino nécessite un **reflash avant un nouveau passage**.
- Le projet n’inclut pas encore de gestion d’erreurs avancée (erreurs de communication, validation complète des scénarios de trajet...).
- Ce dépôt contient des améliorations en cours ; cf TODO dans le code.

---
