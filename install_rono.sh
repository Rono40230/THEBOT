#!/bin/bash
# =============================================================================
# THEBOT - Script de Lancement Personnalisé pour /home/rono/THEBOT/
# Installation et utilisation optimisées pour l'utilisateur rono
# =============================================================================

# Configuration spécifique
THEBOT_PATH="/home/rono/THEBOT"
USER_HOME="/home/rono"

# Couleurs
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
PURPLE='\033[0;35m'
NC='\033[0m'

print_header() {
    clear
    echo -e "${PURPLE}=============================================${NC}"
    echo -e "${CYAN}🤖 THEBOT - Installation Personnalisée${NC}"
    echo -e "${CYAN}   Utilisateur: rono${NC}"
    echo -e "${CYAN}   Chemin: /home/rono/THEBOT/${NC}"
    echo -e "${PURPLE}=============================================${NC}"
    echo
}

check_thebot_exists() {
    if [ -d "$THEBOT_PATH" ]; then
        echo -e "${GREEN}✅ THEBOT trouvé dans $THEBOT_PATH${NC}"
        return 0
    else
        echo -e "${RED}❌ THEBOT non trouvé dans $THEBOT_PATH${NC}"
        return 1
    fi
}

clone_thebot() {
    echo -e "${CYAN}📥 Clonage de THEBOT depuis GitHub...${NC}"
    
    # Aller dans /home/rono
    cd "$USER_HOME" || {
        echo -e "${RED}❌ Impossible d'accéder à $USER_HOME${NC}"
        exit 1
    }
    
    # Cloner
    if git clone https://github.com/Rono40230/THEBOT.git; then
        echo -e "${GREEN}✅ THEBOT cloné avec succès dans $THEBOT_PATH${NC}"
    else
        echo -e "${RED}❌ Erreur lors du clonage${NC}"
        exit 1
    fi
}

setup_thebot() {
    echo -e "${CYAN}🔧 Configuration de THEBOT...${NC}"
    
    cd "$THEBOT_PATH" || {
        echo -e "${RED}❌ Impossible d'accéder à $THEBOT_PATH${NC}"
        exit 1
    }
    
    # Rendre les scripts exécutables
    chmod +x *.sh 2>/dev/null || true
    
    # Installation dépendances Python si environnement virtuel détecté
    if [ -d "venv_thebot" ]; then
        echo -e "${CYAN}📦 Installation dépendances critiques...${NC}"
        source venv_thebot/bin/activate
        pip install --upgrade pip
        pip install matplotlib PyQt6 plotly ipywidgets -q
        pip install -r requirements.txt -q || true
        pip install -e . -q || true
    fi
    
    echo -e "${GREEN}✅ THEBOT configuré${NC}"
}

create_desktop_shortcut() {
    echo -e "${CYAN}🖱️ Création du raccourci desktop...${NC}"
    
    mkdir -p "$USER_HOME/.local/share/applications"
    
    cat > "$USER_HOME/.local/share/applications/thebot-rono.desktop" << EOF
[Desktop Entry]
Name=THEBOT Trading Platform
Comment=Plateforme d'Analyse Trading - Installation Rono
Exec=$THEBOT_PATH/run_thebot.sh
Path=$THEBOT_PATH
Icon=applications-office
Terminal=true
Type=Application
Categories=Office;Finance;
StartupNotify=true
EOF
    
    chmod +x "$USER_HOME/.local/share/applications/thebot-rono.desktop"
    
    echo -e "${GREEN}✅ Raccourci créé ! THEBOT disponible dans les applications${NC}"
}

setup_bash_aliases() {
    echo -e "${CYAN}⚡ Configuration des alias bash...${NC}"
    
    # Vérifier si les alias existent déjà
    if ! grep -q "alias thebot=" "$USER_HOME/.bashrc" 2>/dev/null; then
        echo "
# THEBOT Trading Platform - Alias personnalisés
alias thebot=\"cd $THEBOT_PATH && ./run_thebot.sh\"
alias thebot-native=\"cd $THEBOT_PATH && ./launch_native.sh\"  
alias thebot-jupyter=\"cd $THEBOT_PATH && ./start.sh\"
alias thebot-update=\"cd $THEBOT_PATH && git pull origin main\"
alias thebot-test=\"cd $THEBOT_PATH && python -m pytest tests/unit/indicators/ -v\"
" >> "$USER_HOME/.bashrc"
        
        echo -e "${GREEN}✅ Alias ajoutés à ~/.bashrc${NC}"
        echo -e "${YELLOW}💡 Après installation, utilisez: ${NC}"
        echo -e "${CYAN}   thebot          ${NC}# Menu principal"
        echo -e "${CYAN}   thebot-native   ${NC}# App native directe" 
        echo -e "${CYAN}   thebot-update   ${NC}# Mise à jour"
    else
        echo -e "${YELLOW}⚠️  Alias déjà présents dans ~/.bashrc${NC}"
    fi
}

launch_thebot() {
    echo -e "${GREEN}🚀 Lancement de THEBOT...${NC}"
    
    cd "$THEBOT_PATH" || {
        echo -e "${RED}❌ Impossible d'accéder à $THEBOT_PATH${NC}"
        exit 1
    }
    
    ./run_thebot.sh
}

show_status() {
    echo -e "${CYAN}📊 État de l'installation THEBOT:${NC}"
    echo
    
    if [ -d "$THEBOT_PATH" ]; then
        echo -e "📁 Dossier THEBOT: ${GREEN}✅ $THEBOT_PATH${NC}"
        
        cd "$THEBOT_PATH"
        
        # Vérifier structure
        if [ -d "src" ]; then
            echo -e "🏗️  Code source: ${GREEN}✅ src/${NC}"
        fi
        
        if [ -d "tests" ]; then
            echo -e "🧪 Tests: ${GREEN}✅ tests/${NC}"
        fi
        
        if [ -d "venv_thebot" ]; then
            echo -e "🐍 Environnement virtuel: ${GREEN}✅ venv_thebot/${NC}"
        else
            echo -e "🐍 Environnement virtuel: ${YELLOW}⚠️  Pas encore créé${NC}"
        fi
        
        if [ -f "run_thebot.sh" ]; then
            echo -e "🚀 Script principal: ${GREEN}✅ run_thebot.sh${NC}"
        fi
        
        # Vérifier git
        if [ -d ".git" ]; then
            local git_status=$(git status --porcelain 2>/dev/null | wc -l)
            if [ "$git_status" -eq 0 ]; then
                echo -e "📡 Git: ${GREEN}✅ Synchronisé${NC}"
            else
                echo -e "📡 Git: ${YELLOW}⚠️  Modifications non commitées${NC}"
            fi
        fi
        
    else
        echo -e "📁 Dossier THEBOT: ${RED}❌ Non trouvé${NC}"
    fi
    
    # Vérifier raccourci
    if [ -f "$USER_HOME/.local/share/applications/thebot-rono.desktop" ]; then
        echo -e "🖱️  Raccourci desktop: ${GREEN}✅ Installé${NC}"
    else
        echo -e "🖱️  Raccourci desktop: ${YELLOW}⚠️  Non installé${NC}"
    fi
    
    # Vérifier alias
    if grep -q "alias thebot=" "$USER_HOME/.bashrc" 2>/dev/null; then
        echo -e "⚡ Alias bash: ${GREEN}✅ Configurés${NC}"
    else
        echo -e "⚡ Alias bash: ${YELLOW}⚠️  Non configurés${NC}"
    fi
}

show_menu() {
    echo
    echo -e "${CYAN}Que voulez-vous faire ?${NC}"
    echo "1) 📥 Cloner THEBOT dans /home/rono/THEBOT/"
    echo "2) 🚀 Lancer THEBOT (installation auto si besoin)"
    echo "3) ⚙️  Installation complète (clone + config + raccourcis)"
    echo "4) 📊 Voir l'état de l'installation"
    echo "5) 🔄 Mettre à jour THEBOT"
    echo "6) ❌ Quitter"
    echo
}

main() {
    print_header
    
    # Menu principal
    while true; do
        show_menu
        read -p "Votre choix [1-6]: " choice
        
        case $choice in
            1)
                if check_thebot_exists; then
                    echo -e "${YELLOW}⚠️  THEBOT existe déjà dans $THEBOT_PATH${NC}"
                    read -p "Voulez-vous le supprimer et re-cloner ? [y/N]: " confirm
                    if [[ $confirm =~ ^[Yy]$ ]]; then
                        rm -rf "$THEBOT_PATH"
                        clone_thebot
                        setup_thebot
                    fi
                else
                    clone_thebot
                    setup_thebot
                fi
                ;;
            2)
                if ! check_thebot_exists; then
                    echo -e "${YELLOW}⚠️  THEBOT n'existe pas encore, clonage automatique...${NC}"
                    clone_thebot
                    setup_thebot
                fi
                launch_thebot
                break
                ;;
            3)
                echo -e "${CYAN}🔧 Installation complète...${NC}"
                if ! check_thebot_exists; then
                    clone_thebot
                fi
                setup_thebot
                create_desktop_shortcut
                setup_bash_aliases
                echo -e "${GREEN}✅ Installation complète terminée !${NC}"
                echo -e "${CYAN}💡 Vous pouvez maintenant utiliser 'thebot' en ligne de commande${NC}"
                ;;
            4)
                show_status
                ;;
            5)
                if check_thebot_exists; then
                    cd "$THEBOT_PATH"
                    echo -e "${CYAN}🔄 Mise à jour depuis GitHub...${NC}"
                    git pull origin main
                    echo -e "${GREEN}✅ Mise à jour terminée${NC}"
                else
                    echo -e "${RED}❌ THEBOT n'est pas installé${NC}"
                fi
                ;;
            6)
                echo -e "${GREEN}Au revoir ! 👋${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}Choix invalide. Veuillez choisir 1-6.${NC}"
                ;;
        esac
        
        echo
        read -p "Appuyez sur Entrée pour continuer..."
        print_header
    done
}

# Vérification utilisateur
if [ "$(whoami)" != "rono" ]; then
    echo -e "${YELLOW}⚠️  Ce script est optimisé pour l'utilisateur 'rono'${NC}"
    echo -e "${YELLOW}   Utilisateur actuel: $(whoami)${NC}"
    echo -e "${YELLOW}   Chemin configuré: /home/rono/THEBOT/${NC}"
    echo
    read -p "Continuer quand même ? [y/N]: " confirm
    if [[ ! $confirm =~ ^[Yy]$ ]]; then
        echo "Installation annulée."
        exit 0
    fi
fi

# Lancement
main "$@"