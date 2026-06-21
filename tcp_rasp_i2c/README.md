# Démonstrateur TCP Raspberry Pi + I2C Arduino

Ce dossier contient un exemple de chaîne de communication où :

1. deux cartes Arduino pilotent chacune un feu et exposent leur état en I2C ;
2. un Raspberry Pi lit et écrit les états des Arduino via le bus I2C ;
3. le Raspberry Pi envoie l'état du signal à un ordinateur via une connexion TCP sur le réseau WiFi local.

## Matériel nécessaire

- 1 Raspberry Pi avec I2C activé ;
- 1 ordinateur connecté au même réseau WiFi local que le Raspberry Pi ;
- 1 réseau WiFi local ;
- 2 cartes Arduino compatibles I2C ;
- 2 LED : 1 LED verte et 1 LED rouge ;
- 1 bouton poussoir ;
- résistances adaptées aux LED et au bouton ;
- fils Dupont et breadboard.

## Rôle des fichiers

| Équipement | Code à téléverser ou exécuter | Rôle |
| --- | --- | --- |
| Ordinateur | `computer/main.py` | Serveur TCP qui écoute les messages envoyés par le Raspberry Pi et affiche la couleur du feu. |
| Raspberry Pi | `raspberry_controller/main.py` | Client TCP + contrôleur I2C. Il synchronise les deux Arduino et transmet l'état du feu à l'ordinateur. |
| Arduino avec bouton + LED verte | `arduino_controllers/button_green/button_green.ino` | Esclave I2C de la LED verte. Le bouton permet de demander le changement d'état de la LED verte. |
| Arduino avec LED rouge | `arduino_controllers/red/red.ino` | Esclave I2C de la LED rouge. |

## Adresses et paramètres de communication

### TCP entre l'ordinateur et le Raspberry Pi

- L'ordinateur lance le serveur TCP sur le port `1024`.
- Le Raspberry Pi se connecte à l'adresse IP configurée dans `raspberry_controller/main.py` : `192.168.40.108`.
- Si l'adresse IP de l'ordinateur est différente, modifier la constante `IP` dans `raspberry_controller/main.py` avant de lancer le programme.
- Le port TCP doit rester identique des deux côtés : `1024`.

### I2C entre le Raspberry Pi et les Arduino

Le Raspberry Pi utilise le bus I2C `/dev/i2c-1`, ouvert dans le code avec `SMBus(1)`.

| Fonction | Adresse I2C dans les sketches Arduino | Constante Raspberry Pi à faire correspondre |
| --- | --- | --- |
| Arduino LED rouge | `0x08` dans `arduino_controllers/red/red.ino` | `RED_ADDR = 0x8` |
| Arduino bouton + LED verte | `0x09` dans `arduino_controllers/button_green/button_green.ino` | `GREEN_ADDR = 0x9` |

> Attention : les constantes du fichier `raspberry_controller/main.py` doivent correspondre aux adresses déclarées dans les sketches Arduino. Vérifier et corriger `GREEN_ADDR` et `RED_ADDR` si nécessaire avant l'exécution.

## Modules et logiciels à installer

### Sur l'ordinateur

Python 3 est nécessaire. Le script `computer/main.py` utilise uniquement le module standard `socket`, donc aucun paquet Python externe n'est requis.

Commande de lancement :

```bash
python3 tcp_rasp_i2c/computer/main.py
```

### Sur le Raspberry Pi

Installer Python 3 et le module Python `smbus2` :

```bash
sudo apt update
sudo apt install -y python3 python3-pip i2c-tools
python3 -m pip install smbus2
```

Activer ensuite l'I2C sur le Raspberry Pi :

```bash
sudo raspi-config
```

Dans l'interface, activer `Interface Options` puis `I2C`. Après redémarrage, vérifier la présence des Arduino avec :

```bash
i2cdetect -y 1
```

Les adresses `08` et `09` doivent apparaître si les deux Arduino sont correctement raccordés et alimentés.

### Sur les Arduino

Installer l'IDE Arduino ou `arduino-cli`. Les sketches utilisent la bibliothèque standard `Wire`, incluse avec l'environnement Arduino. Aucune bibliothèque Arduino externe n'est nécessaire.

Téléverser :

- `arduino_controllers/button_green/button_green.ino` sur l'Arduino qui porte le bouton et la LED verte ;
- `arduino_controllers/red/red.ino` sur l'Arduino qui porte la LED rouge.

## Connexions matérielles

### Bus I2C commun

Relier le Raspberry Pi et les deux Arduino sur le même bus I2C :

| Raspberry Pi | Arduino LED verte | Arduino LED rouge | Rôle |
| --- | --- | --- | --- |
| SDA, GPIO 2, broche physique 3 | SDA | SDA | Données I2C |
| SCL, GPIO 3, broche physique 5 | SCL | SCL | Horloge I2C |
| GND | GND | GND | Masse commune |

Important :

- toutes les masses doivent être communes ;
- les Arduino doivent être alimentés correctement ;
- éviter d'injecter du 5 V sur les broches GPIO du Raspberry Pi ;
- selon les cartes Arduino utilisées, prévoir un convertisseur de niveau logique I2C entre le Raspberry Pi en 3,3 V et les Arduino en 5 V.

### Arduino bouton + LED verte

- LED verte sur la broche `2` de l'Arduino, avec une résistance en série ;
- bouton sur l'entrée analogique `A0`, avec un montage qui permet de lire une tension haute lorsque le bouton est appuyé ;
- le seuil de détection du bouton est défini par `TENSION_BUTTON_THRESHOLD = 1000`.

### Arduino LED rouge

- LED rouge sur la broche `13` de l'Arduino, avec une résistance en série si une LED externe est utilisée.

## Ordre de démarrage recommandé

1. Téléverser les deux sketches Arduino sur les bonnes cartes.
2. Raccorder les deux Arduino au bus I2C du Raspberry Pi.
3. Démarrer l'ordinateur et le Raspberry Pi sur le même réseau WiFi local.
4. Relever l'adresse IP de l'ordinateur, par exemple avec `ipconfig` sous Windows ou `ip addr` sous Linux.
5. Mettre cette adresse dans la constante `IP` de `raspberry_controller/main.py`.
6. Lancer le serveur TCP sur l'ordinateur :

   ```bash
   python3 tcp_rasp_i2c/computer/main.py
   ```

7. Lancer le contrôleur sur le Raspberry Pi :

   ```bash
   python3 tcp_rasp_i2c/raspberry_controller/main.py
   ```

## Fonctionnement attendu

- Le Raspberry Pi lit l'état initial des deux Arduino en I2C.
- Si les deux LED sont allumées ou éteintes en même temps, le Raspberry Pi force un état cohérent.
- Lorsqu'un changement est détecté côté LED verte, le Raspberry Pi bascule la LED rouge dans l'état opposé.
- Lorsqu'un changement est détecté côté LED rouge, le Raspberry Pi bascule la LED verte dans l'état opposé.
- À chaque cycle, le Raspberry Pi envoie l'état au serveur TCP de l'ordinateur, qui affiche la couleur du feu.

## Dépannage rapide

- Si `i2cdetect -y 1` ne montre pas `08` et `09`, vérifier SDA, SCL, GND, l'alimentation et les adresses I2C des sketches.
- Si la connexion TCP échoue, vérifier que l'ordinateur et le Raspberry Pi sont sur le même réseau WiFi, que l'adresse `IP` est correcte et que le port `1024` n'est pas bloqué par un pare-feu.
- Si une LED ne réagit pas, vérifier la broche déclarée dans le sketch, la polarité de la LED et la résistance série.
