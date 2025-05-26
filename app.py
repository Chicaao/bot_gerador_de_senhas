import tkinter as tk
from tkinter import messagebox, simpledialog
from password_generator import generate_password
import database

class PasswordBotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerador de senhas")
        self.current_user_id = None #Armazena a ID do usuário conectado
        self.current_user_master_password = None #Armazena a senha mestra para criptografia/descriptografia

        self.create_login_register_frame()

    def create_login_register_frame(self):
        """Cria a interface para login e registro."""
        # Destrói o quadro principal existente, caso exista, para alternar as exibições
        if hasattr(self, 'main_frame'):
            self.main_frame.destroy()

        self.login_register_frame = tk.Frame(self.root, padx=20, pady=20)
        self.login_register_frame.pack()

        tk.Label(self.login_register_frame, text="Nome de usuário:").grid(row=0, column=0, pady=5, sticky='w')
        self.username_entry = tk.Entry(self.login_register_frame, width=30)
        self.username_entry.grid(row=0, column=1, pady=5)

        tk.Label(self.login_register_frame, text="Senha Master:").grid(row=1, column=0, pady=5, sticky='w')
        self.master_password_entry = tk.Entry(self.login_register_frame, show="*", width=30)
        self.master_password_entry.grid(row=1, column=1, pady=5)

        tk.Button(self.login_register_frame, text="Login", command=self.login).grid(row=2, column=0, pady=10, padx=5)
        tk.Button(self.login_register_frame, text="Cadastrar", command=self.register).grid(row=2, column=1, pady=10, padx=5)

    def login(self):
        username = self.username_entry.get()
        master_password = self.master_password_entry.get()

        if not username or not master_password:
            messagebox.showwarning("AVISO","Preencha todos os campos")
            return
        
        user_id, salt = database.authenticate_user(username, master_password)
        if user_id:
            self.current_user_id = user_id
            self.current_user_master_password = master_password
            messagebox.showinfo("Sucesso","Login realizado com sucesso!")
            self.login_register_frame.destroy()
            self.create_main_app_frame()
        else:
            messagebox.showerror("Erro ao fazer o login","Usuário ou senha inválido.")
    
    def register(self):
        username = self.username_entry.get()
        master_password = self.master_password_entry.get()

        if not username or not master_password:
            messagebox.showwarning("Aviso", "Por favor preencha todos os campos")
            return
        
        if database.register_user(username, master_password):
            messagebox.showinfo("Sucesso!", "Usuário registrado com sucesso! Você pode fazer login agora")
            self.username_entry.delete(0, tk.END)
            self.master_password_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Erro no registro", "Nome de usuário já existente")
        
    def create_main_app_frame(self):
        """Cria a interface principal do aplicativo após o login bem-sucedido."""
        self.main_frame = tk.Frame(self.root, padx=20, pady=20)
        self.main_frame.pack()

        #Estrutura para geração de senha
        password_gen_frame = tk.LabelFrame(self.main_frame, text="Gerar nova senha", padx=10, pady=10)
        password_gen_frame.grid(row=0, column=1, pady=5)

        tk.Label(password_gen_frame, text="Descrição do aplicativo onde será usada a senha:").grid(row=0, column=0, pady=5, sticky='w')
        self.description_entry = tk.Entry(password_gen_frame, width=40)
        self.description_entry.grid(row=0, column=1, pady=5)

        tk.Label(password_gen_frame, text="Comprimento da senha:").grid(row=1, column=0, pady=5, sticky='w')
        self.length_var = tk.Spinbox(value="12")
        self.length_spinbox = tk.Spinbox(password_gen_frame, from_=8, to=32, width=5, textvariable=self.length_var)
        self.length_spinbox.grid(row=1, column=1, pady=5, sticky='w')

        self.include_upper = tk.BooleanVar(value=True)
        tk.Checkbutton(password_gen_frame, text="Uppercase (A-Z)", variable=self.include_upper).grid(row=2, column=0, sticky='w')
        self.include_lower = tk.BooleanVar(value=True)
        tk.Checkbutton(password_gen_frame, text="Lowercase (a-z)", variable=self.include_lower).grid(row=2, column=1, sticky='w')
        self.include_digits = tk.BooleanVar(value=True)
        tk.Checkbutton(password_gen_frame, text="Numbers (0-9)", variable=self.include_digits).grid(row=3, column=0, sticky='w')
        self.include_symbols = tk.BooleanVar(value=True)
        tk.Checkbutton(password_gen_frame, text="Symbols (!@#$)", variable=self.include_symbols).grid(row=3, column=1, sticky='w')

        tk.Button(password_gen_frame, text="Gerar e salvar senha", command=self.generate_and_save_password).grid(row=4, column=0, columnspan=2, pady=10)

        tk.Label(password_gen_frame, text="Senha Gerada:").grid(row=5, column=0, pady=5, sticky='w')
        self.generated_password_display = tk.Entry(password_gen_frame, width=40, state='readonly')
        self.generated_password_display.grid(row=5, column=1, pady=5)

        #Botão para visualizar as senhas
        tk.Button(self.main_frame, text="Ver minhas senhas", command=self.show_password_window).grid(row=1, column=0, pady=10)
        tk.Button(self.main_frame, text="Sair", command=self.logout).grid(row=1, column=1, pady=10)

    def generate_and_save_password(self):
        description = self.description_entry.get()
        if not description:
            messagebox.showwarning("AVISO", "Por favor insira uma descrição da senha.")
            return
        try:
            length = int(self.length_var.get())
            if length < 8:
                messagebox.showwarning("AVISO", "A senha precisa de no minimo 8 caracteres")
                return
        except ValueError:
            messagebox.showwarning("AVISO", "Tamanho de senha inválido")
            return

        include_upper = self.include_upper.get()
        include_lower = self.include_lower.get()
        include_digits = self.include_digits.get()
        include_symbols = self.include_symbols.get()

        if not any([include_upper, include_lower, include_digits, include_symbols]):
            messagebox.showwarning("AVISO", "Selecione pelo menos um tipo de caractere para a senha.")

        generated_pwd = generate_password(length, include_upper, include_digits, include_symbols, include_lower)

        if generated_pwd:
            database.save_generated_password(self.current_user_id, description, generated_pwd)
            self.generated_password_display.config(state='normal')
            self.generated_password_display.delete(0, tk.END)
            self.generated_password_display.insert(0, generated_pwd)
            self.generated_password_display.config(state='readonly')
            messagebox.showinfo("Sucesso!", "Senha criada e salva com sucesso!")
            self.description_entry.delete(0, tk.END) #Limpa os campos de descrição
        else: 
            messagebox.showerror("ERRO", "Senha não pode ser criada, verifique novamente.")

    def show_passwords_window(self):
        """Cria uma nova janela para exibir as senhas salvas do usuário."""
        if self.current_user_id is None or self.current_user_master_password is None:
            messagebox.showwarning("Aviso", "Você precisa estar conectado para visualizar suas senhas.")
            return
            
        password_window = tk.Toplevel(self.root)
        password_window.title("Minhas senhas")
        password_window.geometry("400x350")

        tk.Label(password_window, text="Senhas salvas:").pack(pady=10)

        #Usar frame para widget de texto e barra de rolagem
        text_frame = tk.Frame(password_window)
        text_frame.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)

        self.password_list_text = tk.Text(text_frame, wrap=tk.WORD, height=15, width=45)
        self.password_list_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.password_list_text.config(state='disabled')

        #Adicionar barra de rolagem
        scrollbar = tk.Scrollbar(text_frame, command=self.password_list_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.password_list_text.config(yscrollcommand=scrollbar.set)

        self.load_user_passwords()

        #Adicionar botões, copiar selecionados e excluir selecionados
        button_frame = tk.Frame(password_window)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Copiar senhas selecionadas", command=self.copy_selected_passwords).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Excluir senhas selecionadas", command=self.delete_selected_passwords).pack(side=tk.LEFT, padx=5)
    
    def load_user_passwords(self):
        """Carrega e exibe as senhas do usuário no widget de texto."""
        self.password_list_text.config(state='normal') #habilita a escrita
        self.password_list_text.delete(1.0, tk.END) #Limpa o conteudo existente

        user_passwords = database.get_user_passwords(self.current_user_id, self.current_user_master_password)
        if user_passwords:
            #Armazenar senhas com seus IDs exclusivos para exclusão
            self.displayed_passwords_info = [] #Para armazenar (id, descrição e senha)
            for i, (desc, pwd) in enumerate(user_passwords):
                '''Precisamos buscar o ID no banco de dados se quisermos excluí-lo posteriormente
                    Por enquanto, get_user_passwords retorna (description, password).
                    Precisamos modificar database.get_user_passwords para retornar também o ID.
                    Por enquanto, apenas exibiremos e observaremos a necessidade do ID do banco de dados para exclusão.
                '''
                display_text = f"[{i+1}] Descrição: {desc}\n Senha: {pwd}\n\n"
                self.password_list_text.insert(tk.END, display_text)
                #Armazene uma informação simplificada por enquanto, a exclusão real precisa da ID do banco de dados
                self.displayed_passwords_info.append({"index": i+1, "descrição": desc, "senha": pwd})
        else:
            self.password_list_text.insert(tk.END, "Nenhuma senha criada até o momento")
        
        self.password_list_text.config(state='disabled') #Desativa novamente

    def copy_selected_password(self):
        """Copia a senha selecionada do widget Text para a área de transferência."""
        try:
            selected_text = self.password_list_text.get(tk.SEL_FIRST, tk.SEL_LAST)
            #Tente extrair a linha da senha se uma entrada completa for selecionada
            if "Password:" in selected_text:
                password_line = selected_text.split("Password:")[1].s('\n')[0].strip()
                self.root.clipboard_clear()
                self.root.clipboard_append(password_line)
                messagebox.showinfo("Sucesso", "Senha copiada para area de transferencia!")
            else:
                messagebox.showwarning("AVISO", "Selecione uma entrada de senha completa (incluindo “Senha:”) para copiar.")
        except tk.TclError:
            messagebox.showwarning("AVISO", "Nenhum texto foi selecionado para copiar")

    def deleted_selected_password(self):
        """Exclui a entrada de senha selecionada do banco de dados e da interface do usuário."""
        # Isso requer um tratamento mais robusto dos itens selecionados e de seus IDs de banco de dados.
        # Para uma implementação completa, você deve exibir os IDs ou usar uma caixa de listagem
        # em que cada item tenha um link direto para o ID do banco de dados.

        # Como um espaço reservado, solicitaremos ao usuário um índice.
        # Isso não é ideal para a experiência do usuário, mas demonstra o conceito por enquanto.
        selected_index_str = simpledialog.askstring("Excluir senha", "Digite o numero da senha a ser deletada")
        
        if selected_index_str:
            try:
                selected_index = int(selected_index_str)
                if 1 <= selected_index <= len(self.displayed_passwords_info):
                    # Em um aplicativo real, você recuperaria o ID do banco de dados aqui e o passaria para uma função database.delete_password().
                    # Por enquanto, só temos a descrição e a senha em displayed_passwords_info.
                    # Precisamos alterar get_user_passwords para retornar o ID se quisermos excluir diretamente pelo ID.
                    # Como solução temporária, excluiremos por descrição e senha, o que NÃO é ideal
                    # Se as descrições/senhas não forem exclusivas para um usuário.
                    #**TO DO: Modificar database.get_user_passwords para retornar também o ID do banco de dados da senha.
                    # A FAZER: Implementar database.delete_generated_password(password_id)**
                    # Por enquanto, demonstraremos apenas a atualização da interface do usuário e uma mensagem.
                    password_to_delete_info = self.displayed_passwords_info[selected_index - 1]
                    messagebox.showinfo("Excluir", f"Exclusão de senha[{selected_index_str}](Descrição: {self.displayed_passwords_info[selected_index-1]['descrição']})ainda não totalmente implementado pela ID"
                                                        "Primeiro, é necessário buscar o ID real do banco de dados.")
                    # Após a exclusão bem-sucedida do banco de dados:
                    # self.load_user_passwords() # Atualizar a lista                                                    
                else:
                    messagebox.showwarning("ERRO", "Numero de senha inválido")
            except ValueError:
                messagebox.showwarning("ERRO", "Por favor, insira um numero válido")
        else:
            messagebox.showwarning("Informação", "Exclusão cancelada")
        
    def logout(self):
        self.current_user_id = None
        self.current_user_master_password = None
        messagebox.showinfo("Sair", "Você fez logout")
        self.main_frame.destroy()
        self.create_login_register_frame() #Retorna a tela de login/registro

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordBotApp(root)
    root.mainloop()
         
        