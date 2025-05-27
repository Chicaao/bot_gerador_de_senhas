import sqlite3
import hashlib
import contextlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import base64
import os

DATABASE_NAME = 'password_bot.db'

@contextlib.contextmanager

def get_db_cursor():
    """
    Gerenciador de contexto que produz um cursor de banco de dados e garante que a conexão seja fechada.
    """
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        yield cursor #Fornece o cursor a ser usado no bloco ‘with’.
        conn.commit() #Confirmar as alterações se não houver exceções
    except Exception as e:
        if conn:
            conn.rollback() #Reversão em caso de erro
        raise #Aumentar novamente a exceção
    finally: 
        if conn:
            conn.close() #Verifique se a conexão está fechada

# --- Funcçoes de Segurança e Criptografia ---

def hash_password(password):
    '''Gera um hash SHA256 da senha mestra do usuário.'''
    return hashlib.sha256(password.encode()).hexdigest()

def derive_key_from_master_password(master_password, salt):
    """
        Deriva uma chave de criptografia Fernet da senha mestra do usuário e de um sal.      
    """
    kdf_instance = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf_instance.derive(master_password.encode()))
    return key

# --- Funções de Banco de Dados ---

def create_tables():
    """Cria as tabelas de usuários e senhas se elas não existirem."""
    with get_db_cursor() as cursor:
        #Tabela de usuários
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        ''')

        # Tabela de senhas geradas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS generated_passwords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                description TEXT NOT NULL,
                password TEXT NOT NULL, -- CUIDADO: Armazenando senhas em texto puro, em um app real seria criptografado
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        '''
        )

# O commit e close são tratados pelo gerenciador de contexto

def register_user(username, master_password):
    """
    Cadastra um novo usuário no banco de dados.
    Retorna True em sucesso, False em falha (usuário já existe).
    """
    try:
        with get_db_cursor() as cursor:
            password_hash = hash_password(master_password)
            salt = os.urandom(16)
            cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash, salt.hex()))
            return True
    except sqlite3.IntegrityError:
        print(f"Erro: Usuário '{username}' já existe.")
        return False
    except Exception as e:
        print(f"Ocorreu um erro inesperado durante o registro: {e}")
        return False

def authenticate_user(username, master_password):
    """
    Autentica um usuário.
    Retorna o ID do usuário se a autenticação for bem-sucedida, caso contrário, None.
    """
    with get_db_cursor() as cursor:
        password_hash = hash_password(master_password)
        cursor.execute("SELECT id FROM users WHERE username = ? AND password_hash = ?", (username, password_hash))
        user_data = cursor.fecthone()
    if user_data:
        user_id, salt_hex = user_data
        return user_id, bytes.fromhex(salt_hex) #Retorna ID e o salt como bytes
    return None, None

def save_generated_password(user_id, description, password):
    """Salva uma senha gerada para um usuário específico."""
    with get_db_cursor() as cursor:
        #Primeiro, obtenha o salt do usuário
        cursor.execute("")

def get_user_passwords(user_id):
    """Retorna todas as senhas geradas para um usuário específico."""
    with get_db_cursor() as cursor:
        cursor.execute("SELECT description, password FROM generated_passwords WHERE user_id = ?", (user_id,))
        passwords = cursor.fetchall()
    return passwords

#Inicializa o banco de dados e tabelas ao importar
create_tables()



