class AuthManager {
    constructor() {
        this.currentUser = null;
        this.isAuthenticated = false;
        this.init();
    }

    init() {
        this.updateAuthStatus();
        this.setupEventListeners();
    }

    async updateAuthStatus() {
        try {
            const response = await fetch('/api/user/profile', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                this.currentUser = await response.json();
                this.isAuthenticated = true;
                this.updateUI();
            } else {
                this.isAuthenticated = false;
                this.currentUser = null;
                this.updateUI();
            }
        } catch (error) {
            console.error('Erro ao verificar autenticação:', error);
            this.isAuthenticated = false;
            this.updateUI();
        }
    }

    async login(usernameOrEmail, password, rememberMe = false) {
        try {
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    username_or_email: usernameOrEmail,
                    password: password,
                    remember_me: rememberMe
                })
            });

            const result = await response.json();

            if (result.sucesso) {
                this.currentUser = result.usuario;
                this.isAuthenticated = true;
                this.updateUI();
                return {
                    sucesso: true,
                    mensagem: result.mensagem
                };
            } else {
                return {
                    sucesso: false,
                    erro: result.erro
                };
            }
        } catch (error) {
            console.error('Erro ao fazer login:', error);
            return {
                sucesso: false,
                erro: 'Erro ao conectar ao servidor'
            };
        }
    }

    async logout() {
        try {
            const response = await fetch('/api/logout', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const result = await response.json();

            if (result.sucesso) {
                this.currentUser = null;
                this.isAuthenticated = false;
                this.updateUI();
                return {
                    sucesso: true,
                    mensagem: result.mensagem
                };
            }
        } catch (error) {
            console.error('Erro ao fazer logout:', error);
        }

        return {
            sucesso: false,
            erro: 'Erro ao desconectar'
        };
    }

    async register(username, email, password, passwordConfirm) {
        try {
            const response = await fetch('/api/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    username: username,
                    email: email,
                    password: password,
                    password_confirm: passwordConfirm
                })
            });

            const result = await response.json();
            return result;
        } catch (error) {
            console.error('Erro ao registrar:', error);
            return {
                sucesso: false,
                erro: 'Erro ao conectar ao servidor'
            };
        }
    }

    async changePassword(oldPassword, newPassword, newPasswordConfirm) {
        try {
            const response = await fetch('/api/user/change-password', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    old_password: oldPassword,
                    new_password: newPassword,
                    new_password_confirm: newPasswordConfirm
                })
            });

            const result = await response.json();
            return result;
        } catch (error) {
            console.error('Erro ao alterar senha:', error);
            return {
                sucesso: false,
                erro: 'Erro ao conectar ao servidor'
            };
        }
    }

    async updateProfile(email) {
        try {
            const response = await fetch('/api/user/update', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    email: email
                })
            });

            const result = await response.json();

            if (result.sucesso) {
                this.currentUser = result.usuario;
                this.updateUI();
            }

            return result;
        } catch (error) {
            console.error('Erro ao atualizar perfil:', error);
            return {
                sucesso: false,
                erro: 'Erro ao conectar ao servidor'
            };
        }
    }

    updateUI() {
        const authContainer = document.getElementById('auth-container');
        
        if (!authContainer) {
            return;
        }

        if (this.isAuthenticated && this.currentUser) {
            authContainer.innerHTML = `
                <div class="user-menu">
                    <span class="username">Olá, ${this.currentUser.username}!</span>
                    <a href="/user/profile" class="link">Perfil</a>
                    <a href="#" class="link" id="logoutBtn">Sair</a>
                </div>
            `;

            const logoutBtn = document.getElementById('logoutBtn');
            if (logoutBtn) {
                logoutBtn.addEventListener('click', async (e) => {
                    e.preventDefault();
                    await this.logout();
                    window.location.href = '/';
                });
            }
        } else {
            authContainer.innerHTML = `
                <div class="auth-links">
                    <a href="/login" class="btn-login">Login</a>
                    <a href="/register" class="btn-register">Registrar</a>
                </div>
            `;
        }
    }

    setupEventListeners() {
        window.addEventListener('storage', () => {
            this.updateAuthStatus();
        });
    }

    getCurrentUser() {
        return this.currentUser;
    }

    isLoggedIn() {
        return this.isAuthenticated;
    }

    isAdmin() {
        return this.isAuthenticated && this.currentUser && this.currentUser.is_admin;
    }
}

const authManager = new AuthManager();

if (typeof module !== 'undefined' && module.exports) {
    module.exports = AuthManager;
}
