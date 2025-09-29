#!/bin/bash
# Script de démarrage IBKR Client Portal Gateway pour THEBOT

echo "🚀 Démarrage IBKR Client Portal Gateway..."

# Vérifier si Java est installé
if ! command -v java &> /dev/null; then
    echo "❌ Java n'est pas installé. Veuillez installer Java 8 ou supérieur."
    exit 1
fi

# Vérifier la présence du fichier Gateway
if [ ! -f "clientportal.gw/root/conf.yaml" ]; then
    echo "❌ Client Portal Gateway non trouvé."
    echo "📥 Téléchargez-le depuis votre compte IBKR :"
    echo "   Account Management > Settings > API > Settings"
    echo "   Puis décompressez dans ce répertoire."
    exit 1
fi

# Démarrer le Gateway
echo "🔌 Démarrage du Gateway sur https://localhost:5000"
echo "⚠️ IMPORTANT : Vous devrez vous authentifier via navigateur"

cd clientportal.gw
java -cp "build/lib/clientportal.gw.jar" ibkr.web.core.clientportal.gw.GatewayStart &

GATEWAY_PID=$!
echo "🎯 Gateway PID: $GATEWAY_PID"

# Attendre que le gateway soit prêt
echo "⏳ Attente du démarrage du gateway..."
sleep 10

# Test de connectivité
echo "🔍 Test de connectivité..."
if curl -k -s https://localhost:5000/v1/api/iserver/auth/status > /dev/null; then
    echo "✅ Gateway démarré avec succès !"
    echo "🌐 Accédez à https://localhost:5000 pour l'authentification"
    echo "🔗 Ensuite relancez THEBOT pour utiliser les données réelles"
else
    echo "⚠️ Gateway en cours de démarrage... Patientez quelques secondes"
fi

echo "📝 Pour arrêter le gateway : kill $GATEWAY_PID"