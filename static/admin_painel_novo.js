let secaoAtiva = 'dashboard';
let paginaAtual = 1;
let acaoConfirmacao = null;

document.addEventListener('DOMContentLoaded', function() {
    const toggleMenu = document.getElementById('toggle-menu');
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('main-content');

    toggleMenu.addEventListener('click', function() {
        sidebar.classList.toggle('ativo');
        mainContent.classList.toggle('deslocado');
    });

    document.querySelectorAll('.menu-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const secao = this.getAttribute('data-secao');
            mostrarSecao(secao);
            
            document.querySelectorAll('.menu-link').forEach(l => l.classList.remove('ativo'));
            this.classList.add('ativo');
            
            if (window.innerWidth <= 768) {
                sidebar.classList.remove('ativo');
                mainContent.classList.remove('deslocado');
            }
        });
    });

    document.getElementById('usuarios-buscar').addEventListener('input', function() {
        paginaAtual = 1;
        carregarUsuarios();
    });

    document.getElementById('usuarios-filtro').addEventListener('change', function() {
        paginaAtual = 1;
        carregarUsuarios();
    });

    document.getElementById('estab-buscar').addEventListener('input', function() {
        paginaAtual = 1;
        carregarEstabelecimentos();
    });

    document.getElementById('estab-filtro').addEventListener('change', function() {
        paginaAtual = 1;
        carregarEstabelecimentos();
    });

    document.getElementById('msg-filtro').addEventListener('change', function() {
        paginaAtual = 1;
        carregarMensagens();
    });

    document.getElementById('news-filtro').addEventListener('change', function() {
        paginaAtual = 1;
        carregarNewsletter();
    });

    carregarDashboard();
});

function mostrarSecao(secao) {
    document.querySelectorAll('.main-content > div[id]').forEach(el => {
        if (el.id !== 'alertas-container') {
            el.style.display = 'none';
        }
    });

    const secaoEl = document.getElementById(secao);
    if (secaoEl) {
        secaoEl.style.display = 'block';
        secaoAtiva = secao;
        paginaAtual = 1;

        if (secao === 'dashboard') {
            carregarDashboard();
        } else if (secao === 'usuarios') {
            carregarUsuarios();
        } else if (secao === 'estabelecimentos') {
            carregarEstabelecimentos();
        } else if (secao === 'avaliacoes') {
            carregarAvaliacoes();
        } else if (secao === 'mensagens') {
            carregarMensagens();
        } else if (secao === 'newsletter') {
            carregarNewsletter();
        }
    }
}

function carregarDashboard() {
    fetch('/admin/api/dashboard')
        .then(response => response.json())
        .then(dados => {
            const html = `
                <div class="dashboard-grid">
                    <div class="card-stats usuarios">
                        <div class="titulo">Total de Usuários</div>
                        <div class="valor">${dados.usuarios.total}</div>
                        <div class="subtitulo">
                            ${dados.usuarios.ativos} ativos | ${dados.usuarios.inativos} inativos
                        </div>
                        <div class="progressbar">
                            <div class="progressbar-fill" style="width: ${(dados.usuarios.ativos / dados.usuarios.total * 100)}%"></div>
                        </div>
                    </div>

                    <div class="card-stats usuarios">
                        <div class="titulo">Novos Usuários (7 dias)</div>
                        <div class="valor">${dados.usuarios.novos_7dias}</div>
                        <div class="subtitulo">Crescimento recente</div>
                    </div>

                    <div class="card-stats usuarios">
                        <div class="titulo">Usuários com Estabelecimento</div>
                        <div class="valor">${dados.usuarios.com_estabelecimento}</div>
                        <div class="subtitulo">Proprietários ativos</div>
                    </div>

                    <div class="card-stats usuarios">
                        <div class="titulo">Administradores</div>
                        <div class="valor">${dados.usuarios.admins}</div>
                        <div class="subtitulo">Equipe admin</div>
                    </div>

                    <div class="card-stats estabelecimentos">
                        <div class="titulo">Total de Estabelecimentos</div>
                        <div class="valor">${dados.estabelecimentos.total}</div>
                        <div class="subtitulo">
                            ${dados.estabelecimentos.verificados} verificados
                        </div>
                        <div class="progressbar">
                            <div class="progressbar-fill" style="width: ${(dados.estabelecimentos.verificados / dados.estabelecimentos.total * 100)}%"></div>
                        </div>
                    </div>

                    <div class="card-stats estabelecimentos">
                        <div class="titulo">Novos Estabelecimentos (7 dias)</div>
                        <div class="valor">${dados.estabelecimentos.novos_7dias}</div>
                        <div class="subtitulo">Crescimento recente</div>
                    </div>

                    <div class="card-stats estabelecimentos">
                        <div class="titulo">Estabelecimentos Ativos</div>
                        <div class="valor">${dados.estabelecimentos.ativos}</div>
                        <div class="subtitulo">${dados.estabelecimentos.inativos} inativos</div>
                    </div>

                    <div class="card-stats avaliacoes">
                        <div class="titulo">Total de Avaliações</div>
                        <div class="valor">${dados.avaliacoes.total}</div>
                        <div class="subtitulo">Nota média: ${dados.avaliacoes.media}</div>
                    </div>

                    <div class="card-stats mensagens">
                        <div class="titulo">Mensagens de Contato</div>
                        <div class="valor">${dados.mensagens.nao_lidas}</div>
                        <div class="subtitulo">Não lidas de ${dados.mensagens.total}</div>
                    </div>

                    <div class="card-stats">
                        <div class="titulo">Categorias Populares</div>
                        <div style="margin-top: 10px;">
                            ${dados.categorias.map(cat => `
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                    <span style="font-size: 13px;">${cat.categoria}</span>
                                    <span style="font-weight: 700; color: var(--info);">${cat.total}</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
            `;
            document.getElementById('dashboard-stats').innerHTML = html;
        })
        .catch(erro => mostrarAlerta('Erro ao carregar dashboard: ' + erro, 'erro'));
}

function carregarUsuarios() {
    const buscar = document.getElementById('usuarios-buscar').value;
    const filtro = document.getElementById('usuarios-filtro').value;
    
    const url = `/admin/api/usuarios?pagina=${paginaAtual}&buscar=${buscar}&filtro=${filtro}`;
    
    fetch(url)
        .then(response => response.json())
        .then(dados => {
            try { console.log('DEBUG carregarMensagens recebidas:', dados.mensagens); } catch(e) {}
            let html = '';
            
            if (dados.usuarios.length === 0) {
                html = '<tr><td colspan="7" class="sem-dados"><i class="fas fa-user-slash"></i><br>Nenhum usuário encontrado</td></tr>';
            } else {
                html = dados.usuarios.map(u => `
                    <tr>
                        <td><strong>${u.username}</strong></td>
                        <td>${u.email}</td>
                        <td>${u.nome_completo || '-'}</td>
                        <td>
                            <span class="badge ${u.is_active ? 'badge-ativo' : 'badge-inativo'}">
                                ${u.is_active ? 'Ativo' : 'Inativo'}
                            </span>
                        </td>
                        <td>
                            ${u.is_admin ? '<span class="badge badge-admin">Admin</span>' : '-'}
                        </td>
                        <td>${u.estabelecimentos}</td>
                        <td>
                            <div class="acoes">
                                <button class="btn-acao btn-verificar" onclick="toggleAdminUsuario(${u.id}, ${u.is_admin})">
                                    <i class="fas fa-${u.is_admin ? 'user' : 'shield-alt'}"></i>
                                </button>
                                <button class="btn-acao btn-ativar" onclick="toggleAtivoUsuario(${u.id}, ${u.is_active})">
                                    <i class="fas fa-${u.is_active ? 'ban' : 'check'}"></i>
                                </button>
                                <button class="btn-acao btn-deletar" onclick="abrirConfirmacao('deletar', 'usuario', ${u.id}, '${u.username}')">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </td>
                        </tr>
                `).join('');
            }
            
            document.getElementById('usuarios-corpo').innerHTML = html;
            renderizarPaginacao('usuarios', dados.paginas);
        })
        .catch(erro => mostrarAlerta('Erro ao carregar usuários: ' + erro, 'erro'));
}

function carregarEstabelecimentos() {
    const buscar = document.getElementById('estab-buscar').value;
    const filtro = document.getElementById('estab-filtro').value;
    
    const url = `/admin/api/estabelecimentos?pagina=${paginaAtual}&buscar=${buscar}&filtro=${filtro}`;
    
    fetch(url)
        .then(response => response.json())
        .then(dados => {
            let html = '';
            
            if (dados.estabelecimentos.length === 0) {
                html = '<tr><td colspan="7" class="sem-dados"><i class="fas fa-store"></i><br>Nenhum estabelecimento encontrado</td></tr>';
            } else {
                html = dados.estabelecimentos.map(e => `
                    <tr>
                        <td><strong>${e.nome}</strong></td>
                        <td>${e.categoria}</td>
                        <td>${e.usuario}</td>
                        <td>
                            <span class="badge ${e.verificado ? 'badge-verificado' : 'badge-nao-verificado'}">
                                ${e.verificado ? 'Verificado' : 'Não verificado'}
                            </span>
                        </td>
                        <td>
                            <span class="badge ${e.ativo ? 'badge-ativo' : 'badge-inativo'}">
                                ${e.ativo ? 'Ativo' : 'Inativo'}
                            </span>
                        </td>
                        <td>${e.avaliacoes} (${e.nota_media}⭐)</td>
                        <td>
                            <div class="acoes">
                                <button class="btn-acao btn-verificar" onclick="toggleVerificado(${e.id}, ${e.verificado})">
                                    <i class="fas fa-${e.verificado ? 'times' : 'check'}"></i>
                                </button>
                                <button class="btn-acao btn-ativar" onclick="toggleAtivoEstab(${e.id}, ${e.ativo})">
                                    <i class="fas fa-${e.ativo ? 'ban' : 'check'}"></i>
                                </button>
                                <button class="btn-acao btn-deletar" onclick="abrirConfirmacao('deletar', 'estabelecimento', ${e.id}, '${e.nome}')">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </td>
                    </tr>
                `).join('');
            }
            
            document.getElementById('estab-corpo').innerHTML = html;
            renderizarPaginacao('estab', dados.paginas);
        })
        .catch(erro => mostrarAlerta('Erro ao carregar estabelecimentos: ' + erro, 'erro'));
}

function carregarAvaliacoes() {
    const url = `/admin/api/avaliacoes?pagina=${paginaAtual}`;
    
    fetch(url)
        .then(response => response.json())
        .then(dados => {
            let html = '';
            
            if (dados.avaliacoes.length === 0) {
                html = '<tr><td colspan="6" class="sem-dados"><i class="fas fa-star"></i><br>Nenhuma avaliação encontrada</td></tr>';
            } else {
                html = dados.avaliacoes.map(a => `
                    <tr>
                        <td><strong>${a.estabelecimento}</strong></td>
                        <td>${a.usuario}</td>
                        <td>
                            <span style="color: var(--warning); font-weight: 700;">
                                ${'⭐'.repeat(a.nota)}${'☆'.repeat(5 - a.nota)}
                            </span>
                        </td>
                        <td>${a.comentario ? a.comentario.substring(0, 50) + '...' : '-'}</td>
                        <td>${a.criado_em}</td>
                        <td>
                            <button class="btn-acao btn-deletar" onclick="abrirConfirmacao('deletar', 'avaliacao', ${a.id}, 'Avaliação')">
                                <i class="fas fa-trash"></i>
                            </button>
                        </td>
                    </tr>
                `).join('');
            }
            
            document.getElementById('aval-corpo').innerHTML = html;
            renderizarPaginacao('aval', dados.paginas);
        })
        .catch(erro => mostrarAlerta('Erro ao carregar avaliações: ' + erro, 'erro'));
}

function carregarMensagens() {
    const filtro = document.getElementById('msg-filtro').value;
    
    const url = `/admin/api/mensagens?pagina=${paginaAtual}&filtro=${filtro}`;
    
    fetch(url)
        .then(response => response.json())
        .then(dados => {
            let html = '';
            
            if (dados.mensagens.length === 0) {
                html = '<tr><td colspan="7" class="sem-dados"><i class="fas fa-envelope"></i><br>Nenhuma mensagem encontrada</td></tr>';
            } else {
                html = dados.mensagens.map(m => `
                    <tr>
                        <td><strong>${m.nome}</strong></td>
                        <td>${m.email}</td>
                        <td>${m.assunto}</td>
                        <td title="${m.mensagem_completa}">${m.mensagem}</td>
                        <td>${m.criado_em}</td>
                        <td>
                            <span class="badge ${m.lido ? 'badge-ativo' : 'badge-inativo'}">
                                ${m.lido ? 'Lida' : 'Não lida'}
                            </span>
                        </td>
                        <td>
                            <div class="acoes">
                                ${!m.respondida ? `<button class="btn-acao btn-info" onclick="abrirModalResposta(${m.id}, '${m.nome.replace(/'/g, "\\'")}', '${m.email}', '${m.assunto.replace(/'/g, "\\'")}', \`${m.mensagem_completa.replace(/`/g, '\\`')}\`)" style="background-color: #3498db;">
                                    <i class="fas fa-reply"></i>
                                </button>` : ''}
                                ${!m.lido ? `<button class="btn-acao btn-ativar" onclick="marcarLida(${m.id})">
                                    <i class="fas fa-check"></i>
                                </button>` : ''}
                                <button class="btn-acao btn-deletar" onclick="abrirConfirmacao('deletar', 'mensagem', ${m.id}, '${m.assunto}')">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </td>
                    </tr>
                `).join('');
            }
            
            document.getElementById('msg-corpo').innerHTML = html;
            renderizarPaginacao('msg', dados.paginas);
        })
        .catch(erro => mostrarAlerta('Erro ao carregar mensagens: ' + erro, 'erro'));
}

function carregarNewsletter() {
    const filtro = document.getElementById('news-filtro').value;
    
    const url = `/admin/api/newsletter?pagina=${paginaAtual}&filtro=${filtro}`;
    
    fetch(url)
        .then(response => response.json())
        .then(dados => {
            let html = '';
            
            if (dados.newsletter.length === 0) {
                html = '<tr><td colspan="4" class="sem-dados"><i class="fas fa-newspaper"></i><br>Nenhum email encontrado</td></tr>';
            } else {
                html = dados.newsletter.map(n => `
                    <tr>
                        <td>${n.email}</td>
                        <td>
                            <span class="badge ${n.confirmado ? 'badge-ativo' : 'badge-inativo'}">
                                ${n.confirmado ? 'Confirmado' : 'Não confirmado'}
                            </span>
                        </td>
                        <td>${n.criado_em}</td>
                        <td>
                            <button class="btn-acao btn-deletar" onclick="abrirConfirmacao('deletar', 'newsletter', ${n.id}, '${n.email}')">
                                <i class="fas fa-trash"></i>
                            </button>
                        </td>
                    </tr>
                `).join('');
            }
            
            document.getElementById('news-corpo').innerHTML = html;
            renderizarPaginacao('news', dados.paginas);
        })
        .catch(erro => mostrarAlerta('Erro ao carregar newsletter: ' + erro, 'erro'));
}

function renderizarPaginacao(prefixo, totalPaginas) {
    const container = document.getElementById(prefixo + '-paginacao');
    let html = '';
    
    for (let i = 1; i <= totalPaginas; i++) {
        html += `<button class="${i === paginaAtual ? 'ativo' : ''}" onclick="irParaPagina(${i}, '${prefixo}')">${i}</button>`;
    }
    
    container.innerHTML = html;
}

function irParaPagina(pagina, prefixo) {
    paginaAtual = pagina;
    
    if (prefixo === 'usuarios') carregarUsuarios();
    else if (prefixo === 'estab') carregarEstabelecimentos();
    else if (prefixo === 'aval') carregarAvaliacoes();
    else if (prefixo === 'msg') carregarMensagens();
    else if (prefixo === 'news') carregarNewsletter();
}

function toggleAdminUsuario(usuarioId, ehAdmin) {
    fetch(`/admin/api/usuarios/${usuarioId}/toggle-admin`, { method: 'POST' })
        .then(response => response.json())
        .then(dados => {
            mostrarAlerta('Status de admin alterado com sucesso', 'sucesso');
            carregarUsuarios();
        })
        .catch(erro => mostrarAlerta('Erro: ' + erro, 'erro'));
}

function toggleAtivoUsuario(usuarioId, ativo) {
    fetch(`/admin/api/usuarios/${usuarioId}/toggle-ativo`, { method: 'POST' })
        .then(response => response.json())
        .then(dados => {
            mostrarAlerta('Status de ativação alterado com sucesso', 'sucesso');
            carregarUsuarios();
        })
        .catch(erro => mostrarAlerta('Erro: ' + erro, 'erro'));
}

function toggleVerificado(estabId, verificado) {
    fetch(`/admin/api/estabelecimentos/${estabId}/toggle-verificado`, { method: 'POST' })
        .then(response => response.json())
        .then(dados => {
            mostrarAlerta('Status de verificação alterado com sucesso', 'sucesso');
            carregarEstabelecimentos();
        })
        .catch(erro => mostrarAlerta('Erro: ' + erro, 'erro'));
}

function toggleAtivoEstab(estabId, ativo) {
    fetch(`/admin/api/estabelecimentos/${estabId}/toggle-ativo`, { method: 'POST' })
        .then(response => response.json())
        .then(dados => {
            mostrarAlerta('Status de ativação alterado com sucesso', 'sucesso');
            carregarEstabelecimentos();
        })
        .catch(erro => mostrarAlerta('Erro: ' + erro, 'erro'));
}

function marcarLida(mensagemId) {
    fetch(`/admin/api/mensagens/${mensagemId}/marcar-lida`, { method: 'POST' })
        .then(response => response.json())
        .then(dados => {
            mostrarAlerta('Mensagem marcada como lida', 'sucesso');
            carregarMensagens();
        })
        .catch(erro => mostrarAlerta('Erro: ' + erro, 'erro'));
}

function marcarTodasLidas() {
    fetch('/admin/api/mensagens/marcar-todas-lidas', { method: 'POST' })
        .then(response => response.json())
        .then(dados => {
            mostrarAlerta('Todas as mensagens foram marcadas como lidas', 'sucesso');
            carregarMensagens();
        })
        .catch(erro => mostrarAlerta('Erro: ' + erro, 'erro'));
}

function abrirConfirmacao(acao, tipo, id, nome) {
    const mensagensConfirmacao = {
        'deletar-usuario': `Tem certeza que deseja deletar o usuário "${nome}"? Esta ação é irreversível e deletará todos os dados associados.`,
        'deletar-estabelecimento': `Tem certeza que deseja deletar o estabelecimento "${nome}"? Esta ação é irreversível.`,
        'deletar-avaliacao': `Tem certeza que deseja deletar esta avaliação? Esta ação é irreversível.`,
        'deletar-mensagem': `Tem certeza que deseja deletar a mensagem sobre "${nome}"? Esta ação é irreversível.`,
        'deletar-newsletter': `Tem certeza que deseja remover "${nome}" da newsletter?`
    };

    const chave = `${acao}-${tipo}`;
    document.getElementById('modal-mensagem').textContent = mensagensConfirmacao[chave] || 'Tem certeza que deseja executar esta ação?';
    
    acaoConfirmacao = { acao, tipo, id };
    
    document.getElementById('modal-confirmacao').classList.add('ativo');
}

function fecharModal() {
    document.getElementById('modal-confirmacao').classList.remove('ativo');
    acaoConfirmacao = null;
}

function executarAcao() {
    if (!acaoConfirmacao) return;
    
    const { acao, tipo, id } = acaoConfirmacao;
    
    let url = '';
    if (tipo === 'usuario') {
        url = `/admin/api/usuarios/${id}/deletar`;
    } else if (tipo === 'estabelecimento') {
        url = `/admin/api/estabelecimentos/${id}/deletar`;
    } else if (tipo === 'avaliacao') {
        url = `/admin/api/avaliacoes/${id}/deletar`;
    } else if (tipo === 'mensagem') {
        url = `/admin/api/mensagens/${id}/deletar`;
    } else if (tipo === 'newsletter') {
        url = `/admin/api/newsletter/${id}/deletar`;
    }
    
    fetch(url, { method: 'DELETE' })
        .then(response => response.json())
        .then(dados => {
            mostrarAlerta(dados.mensagem || 'Ação executada com sucesso', 'sucesso');
            fecharModal();
            
            if (tipo === 'usuario') carregarUsuarios();
            else if (tipo === 'estabelecimento') carregarEstabelecimentos();
            else if (tipo === 'avaliacao') carregarAvaliacoes();
            else if (tipo === 'mensagem') carregarMensagens();
            else if (tipo === 'newsletter') carregarNewsletter();
        })
        .catch(erro => mostrarAlerta('Erro: ' + erro, 'erro'));
}

function mostrarAlerta(mensagem, tipo) {
    const container = document.getElementById('alertas-container');
    const id = Date.now();
    
    const html = `
        <div class="alerta alerta-${tipo}" id="alerta-${id}">
            ${mensagem}
        </div>
    `;
    
    container.insertAdjacentHTML('beforeend', html);
    
    setTimeout(() => {
        const alerta = document.getElementById('alerta-' + id);
        if (alerta) {
            alerta.remove();
        }
    }, 5000);
}

document.addEventListener('click', function(e) {
    if (e.target === document.getElementById('modal-confirmacao')) {
        fecharModal();
    }
    if (e.target === document.getElementById('modal-responder-mensagem')) {
        fecharModalResposta();
    }
});

function abrirModalResposta(mensagemId, nome, email, assunto, mensagem) {
    document.getElementById('resp-nome').textContent = nome;
    document.getElementById('resp-email').textContent = email;
    document.getElementById('resp-assunto').textContent = assunto;
    document.getElementById('resp-mensagem').textContent = mensagem;
    document.getElementById('resposta-texto').value = '';
    document.getElementById('contador-caracteres').textContent = '0';
    
    const modal = document.getElementById('modal-responder-mensagem');
    modal.classList.add('ativo');
    modal.dataset.mensagemId = mensagemId;
}

function fecharModalResposta() {
    const modal = document.getElementById('modal-responder-mensagem');
    modal.classList.remove('ativo');
    modal.dataset.mensagemId = '';
    document.getElementById('resposta-texto').value = '';
    document.getElementById('contador-caracteres').textContent = '0';
}

document.getElementById('resposta-texto')?.addEventListener('input', function() {
    const maxChars = 5000;
    const currentChars = this.value.length;
    document.getElementById('contador-caracteres').textContent = currentChars;
    
    if (currentChars > maxChars) {
        this.value = this.value.substring(0, maxChars);
        document.getElementById('contador-caracteres').textContent = maxChars;
    }
});

function enviarResposta() {
    const mensagemId = document.getElementById('modal-responder-mensagem').dataset.mensagemId;
    const resposta = document.getElementById('resposta-texto').value.trim();
    
    if (!mensagemId) {
        mostrarAlerta('ID da mensagem não encontrado', 'erro');
        return;
    }
    
    if (!resposta || resposta.length < 5) {
        mostrarAlerta('A resposta deve ter pelo menos 5 caracteres', 'aviso');
        return;
    }
    
    if (resposta.length > 5000) {
        mostrarAlerta('A resposta não pode ter mais de 5000 caracteres', 'aviso');
        return;
    }
    
    const botaoEnviar = event.target;
    botaoEnviar.disabled = true;
    botaoEnviar.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Enviando...';
    
    fetch(`/admin/api/mensagens/${mensagemId}/responder`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ resposta: resposta })
    })
    .then(response => response.json())
    .then(dados => {
        if (dados.erro) {
            mostrarAlerta('Erro: ' + dados.erro, 'erro');
            botaoEnviar.disabled = false;
            botaoEnviar.innerHTML = '<i class="fas fa-paper-plane"></i> Enviar Resposta';
            return;
        }
        
        mostrarAlerta('Resposta enviada com sucesso!', 'sucesso');
        fecharModalResposta();
        carregarMensagens();
        botaoEnviar.disabled = false;
        botaoEnviar.innerHTML = '<i class="fas fa-paper-plane"></i> Enviar Resposta';
    })
    .catch(erro => {
        mostrarAlerta('Erro ao enviar resposta: ' + erro, 'erro');
        botaoEnviar.disabled = false;
        botaoEnviar.innerHTML = '<i class="fas fa-paper-plane"></i> Enviar Resposta';
    });
}
