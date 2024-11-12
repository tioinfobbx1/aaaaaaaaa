#!/bin/bash

# Caminho padrão local
LOCAL_PATH="."

# Lista de servidores com IP, porta, usuário e caminho padrão
SERVERS=(
    "Server 4N Primeiro|101.99.75.122:20203|root|/root/correios"  # Nome | IP:Porta | Usuário | Caminho
    "Server 12N Atual|111.90.148.166:20203|root|/root/correios"
    "Server TIO NOVO|148.113.178.203:22|ubuntu|/home/ubuntu/correios"
)

# Variáveis para IP, porta, usuário e caminho
SERVER_IP=""
SERVER_PORT=""
SERVER_USER=""
SERVER_PATH=""

# Função para escolher o servidor
choose_server() {
    echo "====== Escolha o Servidor ======"
    PS3="Selecione o servidor: "
    
    # Cria a lista apenas com os nomes para o menu
    server_names=()
    for entry in "${SERVERS[@]}"; do
        server_names+=("$(echo "$entry" | cut -d'|' -f1)")
    done

    select server_name in "${server_names[@]}"; do
        if [[ -n "$server_name" ]]; then
            selected_entry="${SERVERS[$((REPLY - 1))]}"
            SERVER_IP=$(echo "$selected_entry" | cut -d'|' -f2 | cut -d':' -f1)
            SERVER_PORT=$(echo "$selected_entry" | cut -d'|' -f2 | cut -d':' -f2)
            SERVER_USER=$(echo "$selected_entry" | cut -d'|' -f3)
            SERVER_PATH=$(echo "$selected_entry" | cut -d'|' -f4)
            echo "Servidor selecionado: $server_name ($SERVER_IP:$SERVER_PORT, Usuário: $SERVER_USER, Caminho: $SERVER_PATH)"
            break
        else
            echo "Opção inválida. Tente novamente."
        fi
    done
}

# Função para sincronizar do servidor para o PC
sync_server_to_pc() {
    if [[ -z "$SERVER_IP" || -z "$SERVER_PORT" || -z "$SERVER_USER" || -z "$SERVER_PATH" ]]; then
        echo "Nenhum servidor selecionado. Use a opção 3 para selecionar um servidor."
        return
    fi
    echo "Sincronizando do servidor para o PC, ignorando pastas venv, flask_session e __pycache__..."
    
    rsync -avz --progress -e "ssh -p ${SERVER_PORT}" \
        --exclude "venv/" \
        --exclude "flask_session/" \
        --exclude "__pycache__/" \
        --exclude "*/__pycache__/" \
        "${SERVER_USER}@${SERVER_IP}:${SERVER_PATH}/" "${LOCAL_PATH}/"
    
    echo "Sincronização do servidor para o PC concluída!"
}

# Função para sincronizar do PC para o servidor
sync_pc_to_server() {
    if [[ -z "$SERVER_IP" || -z "$SERVER_PORT" || -z "$SERVER_USER" || -z "$SERVER_PATH" ]]; then
        echo "Nenhum servidor selecionado. Use a opção 3 para selecionar um servidor."
        return
    fi
    echo "Sincronizando do PC para o servidor, ignorando pastas venv, flask_session e __pycache__..."
    
    rsync -avz --progress -e "ssh -p ${SERVER_PORT}" \
        --exclude "venv/" \
        --exclude "flask_session/" \
        --exclude "__pycache__/" \
        --exclude "*/__pycache__/" \
        "${LOCAL_PATH}/" "${SERVER_USER}@${SERVER_IP}:${SERVER_PATH}/"
    
    echo "Sincronização do PC para o servidor concluída!"
}

# Função para sincronizar configurações NGINX do PC para o servidor
sync_nginx_config() {
    if [[ -z "$SERVER_IP" || -z "$SERVER_PORT" || -z "$SERVER_USER" ]]; then
        echo "Nenhum servidor selecionado. Use a opção 3 para selecionar um servidor."
        return
    fi
    echo "Sincronizando configuração NGINX do PC para o servidor com sudo..."
    
    rsync -avz --progress -e "ssh -p ${SERVER_PORT}" \
        "./nginx/" "${SERVER_USER}@${SERVER_IP}:/tmp/nginx_config/"
    
    ssh -p ${SERVER_PORT} "${SERVER_USER}@${SERVER_IP}" "sudo cp -r /tmp/nginx_config/* /etc/nginx/ && sudo rm -rf /tmp/nginx_config"
    
    echo "Configuração NGINX sincronizada com sucesso!"
}


# Função para criar backup local
backup_local() {
    echo "Criando backup da pasta local..."
    
    # Nome do arquivo de backup com timestamp
    BACKUP_NAME="backup_$(date +%Y%m%d_%H%M%S).zip"
    
    # Comando para criar o ZIP ignorando as pastas específicas
    zip -r "${BACKUP_NAME}" . -x "venv/*" "flask_session/*" "__pycache__/*" "*/__pycache__/*" "*/venv/*" "*/flask_session/*"

    echo "Backup concluído: ${BACKUP_NAME}"
}

# Menu interativo
while true; do
    clear
    echo "====== Menu de Sincronização ======"
    echo "1. Sync SERVER => LOCAL"
    echo "2. Sync LOCAL => SERVER"
    echo "3. SELECIONAR SERVIDOR"
    echo "4. BACKUP LOCAL ZIP"
    echo "5. CONFIGURAR NGINX"
    echo "6. Sair"
    echo "==================================="
    read -p "Escolha uma opção: " option
    
    case $option in
        1) 
            sync_server_to_pc
            read -p "Pressione Enter para continuar..."
            ;;
        2) 
            sync_pc_to_server
            read -p "Pressione Enter para continuar..."
            ;;
        3)
            choose_server
            read -p "Pressione Enter para continuar..."
            ;;
        4) 
            backup_local
            read -p "Pressione Enter para continuar..."
            ;;
        5) 
            sync_nginx_config
            read -p "Pressione Enter para continuar..."
            ;;
        6) 
            echo "Saindo..."
            exit 0
            ;;
        *) 
            echo "Opção inválida! Tente novamente."
            read -p "Pressione Enter para continuar..."
            ;;
    esac
done
