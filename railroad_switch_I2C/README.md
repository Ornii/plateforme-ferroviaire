# Plateforme d’aiguillage ferroviaire (Arduino + Raspberry Pi)

Ce module implémente le pilotage d’un aiguillage ferroviaire miniature basé sur une architecture distribuée :

- **Arduino** : contrôle bas niveau des actionneurs et capteurs (servo, LEDs, capteurs Hall).
- **Raspberry Pi** : logique métier de circulation, routage d’itinéraire et orchestration des échanges I2C.

L’objectif est de séparer clairement la logique temps réel matérielle (microcontrôleur) de la logique de décision (contrôleur Python).

---

## Sommaire

1. [Architecture](#architecture)
2. [Prérequis matériels](#prérequis-matériels)
3. [Prérequis logiciels](#prérequis-logiciels)
4. [Installation](#installation)
5. [Exécution](#exécution)
6. [Configuration](#configuration)
7. [Limites connues](#limites-connues)

---

## Architecture

```text
railroad_switch/
├── arduino_controller/
│   └── firmware/
│       └── firmware.ino
└── raspberry_controller/
    ├── run_controller.py
    ├── bootstrap/
    ├── communication/
    ├── domain/
    └── infrastructure/
```

### Responsabilités principales

- `arduino_controller/firmware/firmware.ino` : firmware embarqué Arduino (I2C esclave).
- `raspberry_controller/run_controller.py` : point d’entrée du contrôleur Raspberry (I2C maître).
- `raspberry_controller/domain/` : logique métier (état du train, protocole, règles d’aiguillage).
- `raspberry_controller/infrastructure/` : interfaces matérielles (capteurs, signaux, aiguillage).

---

## Prérequis matériels

- 1 × Raspberry Pi avec interface **I2C activée**
- 1 × Arduino connecté en I2C
- Câblage I2C fonctionnel entre Raspberry Pi et Arduino
- 1 × servo d’aiguillage
- LEDs de signalisation (ex. rouge/verte)
- Capteurs Hall pour détection de passage

---

## Prérequis logiciels

### Côté Arduino

- Arduino IDE
- Bibliothèques :
  - `Wire`
  - `Servo`

### Côté Raspberry Pi

- Python **3.10+**
- Dépendance Python :
  - `smbus2`

Installation :

```bash
pip install smbus2
```

---

## Installation

### Déployer le firmware Arduino

1. Ouvrir `arduino_controller/firmware/firmware.ino` dans l’Arduino IDE.
2. Compiler le firmware.
3. Téléverser vers la carte Arduino.


## Exécution

Depuis `railroad_switch/` :

```bash
python3 raspberry_controller/run_controller.py
```

> Important : exécuter la commande depuis la racine `railroad_switch/` pour permettre les imports

---

## Configuration

Les paramètres de circulation (position initiale, objectif, stratégie d’aiguillage, etc.) sont définis dans les modules Python du contrôleur Raspberry (`domain/` et point d’entrée).

Selon votre câblage, adaptez notamment :

- l’adresse I2C,
- la cartographie des capteurs,
- les numéros de broches associés aux signaux et à l’aiguillage.

---

## Limites connues

- Certains scénarios nécessitent encore une réinitialisation/reprogrammation côté firmware.
- La gestion d’erreurs I2C et la résilience globale peuvent être renforcées.
- Le projet est en évolution ; des optimisations sont en cours sur le comportement métier et la robustesse.
