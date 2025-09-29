# 📚 Guide d'Installation IBKR Client Portal Gateway

## 🎯 **Objectif**
Connecter THEBOT aux données réelles d'Interactive Brokers via l'API Web.

## 📋 **Prérequis**
- ✅ Compte IBKR actif
- ✅ Java 8 ou supérieur installé
- ✅ THEBOT installé et fonctionnel

## 🔧 **Étapes d'Installation**

### **1. Téléchargement du Client Portal Gateway**

1. **Connectez-vous à votre compte IBKR** :
   - Allez sur https://www.interactivebrokers.com
   - Connexion avec vos identifiants

2. **Accédez aux paramètres API** :
   ```
   Account Management → Settings → API → Settings
   ```

3. **Téléchargez le Client Portal Gateway** :
   - Cliquez sur "Download Client Portal Gateway"
   - Sauvegardez le fichier ZIP

### **2. Installation dans THEBOT**

1. **Décompressez dans le répertoire THEBOT** :
   ```bash
   cd /home/rono/THEBOT
   unzip clientportal.gw.zip
   ```

2. **Structure attendue** :
   ```
   /home/rono/THEBOT/
   ├── clientportal.gw/
   │   ├── build/
   │   │   └── lib/
   │   │       └── clientportal.gw.jar
   │   ├── root/
   │   │   └── conf.yaml
   │   └── bin/
   └── launch_ibkr_gateway.sh ✅
   ```

### **3. Configuration**

1. **Éditez le fichier de configuration** (optionnel) :
   ```bash
   nano clientportal.gw/root/conf.yaml
   ```

2. **Configuration recommandée** :
   ```yaml
   proxyRemoteSsl: true
   proxyRemotePort: 5000
   listenPort: 5000
   listenSsl: true
   ```

### **4. Démarrage**

1. **Lancez le Gateway** :
   ```bash
   ./launch_ibkr_gateway.sh
   ```

2. **Authentification** :
   - Ouvrez https://localhost:5000 dans votre navigateur
   - Acceptez le certificat SSL self-signed
   - Connectez-vous avec vos identifiants IBKR
   - Validez l'authentification 2FA si activée

3. **Vérification** :
   ```bash
   # Test de l'API
   curl -k https://localhost:5000/v1/api/iserver/auth/status
   ```

### **5. Intégration THEBOT**

1. **Relancez THEBOT** :
   ```bash
   /home/rono/THEBOT/.venv/bin/python launch_dash_modular.py
   ```

2. **Vérifiez le statut** :
   - Le badge devrait afficher : 🔗 **"IBKR Connecté"**
   - Les logs montrent : **"Données réelles activées"**

## 🔍 **Dépannage**

### **Erreur : "Connection refused"**
- ✅ Gateway pas démarré → `./launch_ibkr_gateway.sh`
- ✅ Mauvais port → Vérifiez conf.yaml (port 5000)

### **Erreur : "Authentication failed"**
- ✅ Non connecté → https://localhost:5000
- ✅ Session expirée → Reconnectez-vous via navigateur

### **Erreur : "Java ClassNotFoundException"**
- ✅ Structure incorrecte → Vérifiez clientportal.gw/build/lib/
- ✅ Fichier JAR manquant → Retéléchargez depuis IBKR

### **Erreur : "SSL Certificate"**
- ✅ Acceptez le certificat dans le navigateur
- ✅ Ajoutez `-k` aux commandes curl

## 📊 **Données Disponibles**

Une fois connecté, THEBOT aura accès à :

### **📈 Market Data**
- Prix temps réel (bid/ask/last)
- Données historiques OHLCV
- Volume et liquidité
- Carnet d'ordres Level II

### **💼 Compte**
- Solde et positions
- P&L temps réel
- Marge disponible
- Historique des transactions

### **📰 Informations**
- Actualités financières
- Données fondamentales
- Calendrier économique
- Analyse de sentiment

## 🎯 **Avantages THEBOT + IBKR**

- ✅ **Données réelles** au lieu de simulation
- ✅ **160 marchés** dans 36 pays
- ✅ **Toutes classes d'actifs** (Actions, Options, Futures, Forex)
- ✅ **Trading en un clic** (si activé)
- ✅ **Coûts réduits** (pas de frais API supplémentaires)

## ⚠️ **Sécurité**

- 🔒 **Gateway local uniquement** (localhost:5000)
- 🔒 **Authentification IBKR** requise
- 🔒 **SSL/TLS** pour toutes communications
- 🔒 **Mode démo** par défaut pour trading

## 📞 **Support**

- 📧 **IBKR API Support** : Ticket via compte IBKR
- 📚 **Documentation** : https://www.interactivebrokers.com/campus/ibkr-api-page/
- 🎓 **Cours** : IBKR Traders' Academy API