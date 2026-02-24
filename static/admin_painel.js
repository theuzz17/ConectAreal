let secaoAtual = 'estabelecimentos';
let dadosEstabelecimentos = [];
let dadosPrestadores = [];
let dadosMensagens = [];
let itemSelecionadoParaDeletar = null;
let tipoItemSelecionado = null;
let modalFormulario, modalConfirmacao, btnAdicionar, btnFecharModal, btnCancelarConfirm, btnConfirmarExclusao, tituloModal, formularioModal, tituloPagina, itensMenu, secoesConteudo;

function initAdmin() {
    itensMenu = document.querySelectorAll('.item-menu');
    secoesConteudo = document.querySelectorAll('.secao-conteudo');
    modalFormulario = document.getElementById('modalFormulario');
    modalConfirmacao = document.getElementById('modalConfirmacao');
    btnAdicionar = document.getElementById('btnAdicionar');
    btnFecharModal = document.querySelector('.botao-fechar');
    btnCancelarConfirm = document.getElementById('btnCancelar');
    btnConfirmarExclusao = document.getElementById('btnConfirmar');
    tituloModal = document.getElementById('tituloModal');
    formularioModal = document.getElementById('formularioModal');
    tituloPagina = document.getElementById('titulo-pagina');

    itensMenu.forEach(item => {
        item.addEventListener('click', (evento) => {
            evento.preventDefault();
            const secao = item.dataset.secao;
            trocarSecao(secao);
        });
    });

    function trocarSecao(secao) {
        secaoAtual = secao;

        itensMenu.forEach(item => item.classList.remove('ativo'));
        const ativo = document.querySelector(`[data-secao="${secao}"]`);
        if (ativo) ativo.classList.add('ativo');

        secoesConteudo.forEach(sec => sec.classList.remove('ativa'));
        const secEl = document.getElementById(secao);
        if (secEl) secEl.classList.add('ativa');

        switch(secao) {
            case 'estabelecimentos':
                if (tituloPagina) tituloPagina.textContent = 'Gerenciar Estabelecimentos';
                carregarEstabelecimentos();
                break;
            case 'prestadores':
                if (tituloPagina) tituloPagina.textContent = 'Gerenciar Prestadores';
                carregarPrestadores();
                break;
            case 'mensagens':
                if (tituloPagina) tituloPagina.textContent = 'Mensagens de Contato';
                carregarMensagens();
                break;
        }
    }

    if (btnAdicionar) {
        btnAdicionar.addEventListener('click', () => {
            if (secaoAtual === 'estabelecimentos') {
                abrirModalEstabelecimento();
            } else if (secaoAtual === 'prestadores') {
                abrirModalPrestador();
            }
        });
    }

    if (btnFecharModal) btnFecharModal.addEventListener('click', fecharModal);
    if (btnCancelarConfirm) btnCancelarConfirm.addEventListener('click', fecharModalConfirmacao);

    document.addEventListener('click', (evento) => {
        if (evento.target === modalFormulario) {
            fecharModal();
        }
        if (evento.target === modalConfirmacao) {
            fecharModalConfirmacao();
        }
    });

    
    const buscaEstab = document.getElementById('buscaEstabelecimentos');
    if (buscaEstab) {
        buscaEstab.addEventListener('input', (evento) => {
            const termo = evento.target.value.toLowerCase();
            const filtro = document.getElementById('filtroCategoria') ? document.getElementById('filtroCategoria').value : '';

            const filtrados = dadosEstabelecimentos.filter(est => {
                const matchTermo = (est.titulo || '').toLowerCase().includes(termo) || 
                                  (est.descricao || '').toLowerCase().includes(termo);
                const matchFiltro = filtro === '' || est.categoria === filtro;
                return matchTermo && matchFiltro;
            });

            if (filtrados.length === 0) {
                const lista = document.getElementById('listaEstabelecimentos');
                if (lista) lista.innerHTML = `\n            <div class="cartao-vazio">\n                <div class="icone">🔍</div>\n                <p>Nenhum estabelecimento encontrado</p>\n            </div>\n        `;
                return;
            }

            let html = '<table class="tabela"><thead><tr><th>ID</th><th>Título</th><th>Categoria</th><th>Localização</th><th>Avaliação</th><th>Ações</th></tr></thead><tbody>';

            filtrados.forEach(est => {
                html += `\n            <tr>\n                <td>${est.id}</td>\n                <td>${est.titulo}</td>\n                <td><span class="badge badge-categoria">${est.categoria}</span></td>\n                <td>${est.localizacao}</td>\n                <td>⭐ ${est.avaliacao.toFixed(1)}</td>\n                <td>\n                    <div class="acoes-tabela">\n                        <button class="botao-editar" onclick="abrirModalEstabelecimento(${est.id})">Editar</button>\n                        <button class="botao-deletar" onclick="confirmarDeletarEstabelecimento(${est.id})">Deletar</button>\n                    </div>\n                </td>\n            </tr>\n        `;
            });

            html += '</tbody></table>';
            const lista = document.getElementById('listaEstabelecimentos');
            if (lista) lista.innerHTML = html;
        });
    }

    const buscaPrest = document.getElementById('buscaPrestadores');
    if (buscaPrest) {
        buscaPrest.addEventListener('input', (evento) => {
            const termo = evento.target.value.toLowerCase();

            const filtrados = dadosPrestadores.filter(prest => {
                return (prest.nome || '').toLowerCase().includes(termo) || 
                       (prest.profissao || '').toLowerCase().includes(termo);
            });

            if (filtrados.length === 0) {
                const lista = document.getElementById('listaPrestadores');
                if (lista) lista.innerHTML = `\n            <div class="cartao-vazio">\n                <div class="icone">🔍</div>\n                <p>Nenhum prestador encontrado</p>\n            </div>\n        `;
                return;
            }

            let html = '<table class="tabela"><thead><tr><th>ID</th><th>Nome</th><th>Profissão</th><th>Localização</th><th>Telefone</th><th>Status</th><th>Ações</th></tr></thead><tbody>';

            filtrados.forEach(prest => {
                const statusBadge = prest.verificado ? 
                    '<span class="badge badge-verificado">✓ Verificado</span>' : 
                    '<span class="badge badge-nao-verificado">✗ Não Verificado</span>';

                html += `\n            <tr>\n                <td>${prest.id}</td>\n                <td>${prest.nome}</td>\n                <td>${prest.profissao}</td>\n                <td>${prest.localizacao}</td>\n                <td>${prest.telefone}</td>\n                <td>${statusBadge}</td>\n                <td>\n                    <div class="acoes-tabela">\n                        <button class="botao-editar" onclick="abrirModalPrestador(${prest.id})">Editar</button>\n                        <button class="botao-deletar" onclick="confirmarDeletarPrestador(${prest.id})">Deletar</button>\n                    </div>\n                </td>\n            </tr>\n        `;
            });

            html += '</tbody></table>';
            const lista = document.getElementById('listaPrestadores');
            if (lista) lista.innerHTML = html;
        });
    }

    const buscaMens = document.getElementById('buscaMensagens');
    if (buscaMens) {
        buscaMens.addEventListener('input', (evento) => {
            const termo = evento.target.value.toLowerCase();

            const filtrados = dadosMensagens.filter(msg => {
                return (msg.nome || '').toLowerCase().includes(termo) || 
                       (msg.assunto || '').toLowerCase().includes(termo) ||
                       (msg.email || '').toLowerCase().includes(termo);
            });

            if (filtrados.length === 0) {
                const lista = document.getElementById('listaMensagens');
                if (lista) lista.innerHTML = `\n            <div class="cartao-vazio">\n                <div class="icone">🔍</div>\n                <p>Nenhuma mensagem encontrada</p>\n            </div>\n        `;
                return;
            }

            let html = '';

            filtrados.forEach((msg, idx) => {
                const data = new Date(msg.data).toLocaleDateString('pt-BR');
                const indexOriginal = dadosMensagens.indexOf(msg);
                html += `\n            <div class="info-mensagem">\n                <div class="dados-mensagem">\n                    <div class="remetente">${msg.nome}</div>\n                    <div class="assunto-mensagem"><strong>Assunto:</strong> ${msg.assunto}</div>\n                    <div style="margin-bottom: 8px;"><strong>Mensagem:</strong> ${msg.mensagem}</div>\n                    <div style="margin-bottom: 8px;"><strong>Email:</strong> ${msg.email}</div>\n                    ${msg.telefone ? `<div style="margin-bottom: 8px;"><strong>Telefone:</strong> ${msg.telefone}</div>` : ''}\n                    <div class="data-mensagem">Recebida em: ${data}</div>\n                </div>\n                <button class="botao-deletar" onclick="confirmarDeletarMensagem(${indexOriginal})">Deletar</button>\n            </div>\n        `;
            });

            const lista = document.getElementById('listaMensagens');
            if (lista) lista.innerHTML = html;
        });
    }

    if (btnConfirmarExclusao) {
        btnConfirmarExclusao.addEventListener('click', async () => {
            if (tipoItemSelecionado === 'estabelecimento') {
                try {
                    const resposta = await fetch(`/api/admin/estabelecimentos/${itemSelecionadoParaDeletar}`, {
                        method: 'DELETE'
                    });
                    const resultado = await resposta.json();
                    if (resultado.sucesso) {
                        fecharModalConfirmacao();
                        carregarEstabelecimentos();
                    }
                } catch (erro) {
                    console.error('Erro ao deletar:', erro);
                }
            } else if (tipoItemSelecionado === 'prestador') {
                try {
                    const resposta = await fetch(`/api/admin/prestadores/${itemSelecionadoParaDeletar}`, {
                        method: 'DELETE'
                    });
                    const resultado = await resposta.json();
                    if (resultado.sucesso) {
                        fecharModalConfirmacao();
                        carregarPrestadores();
                    }
                } catch (erro) {
                    console.error('Erro ao deletar:', erro);
                }
            } else if (tipoItemSelecionado === 'mensagem') {
                try {
                    const resposta = await fetch(`/api/admin/mensagens/${itemSelecionadoParaDeletar}`, {
                        method: 'DELETE'
                    });
                    const resultado = await resposta.json();
                    if (resultado.sucesso) {
                        fecharModalConfirmacao();
                        carregarMensagens();
                    }
                } catch (erro) {
                    console.error('Erro ao deletar:', erro);
                }
            }
        });
    }

    carregarEstabelecimentos();
}

if (document.readyState !== 'loading') {
    if (document.getElementById('titulo-pagina') || document.getElementById('listaEstabelecimentos')) initAdmin();
} else {
    document.addEventListener('DOMContentLoaded', () => {
        if (document.getElementById('titulo-pagina') || document.getElementById('listaEstabelecimentos')) initAdmin();
    });
}

async function carregarEstabelecimentos() {
    try {
        const resposta = await fetch('/api/admin/estabelecimentos');
        dadosEstabelecimentos = await resposta.json();
        renderizarEstabelecimentos();
    } catch (erro) {
        console.error('Erro ao carregar estabelecimentos:', erro);
    }
}

function renderizarEstabelecimentos() {
    const listaEstabelecimentos = document.getElementById('listaEstabelecimentos');

    if (dadosEstabelecimentos.length === 0) {
        listaEstabelecimentos.innerHTML = `
            <div class="cartao-vazio">
                <div class="icone">🏪</div>
                <p>Nenhum estabelecimento cadastrado</p>
            </div>
        `;
        return;
    }

    let html = '<table class="tabela"><thead><tr><th>ID</th><th>Título</th><th>Categoria</th><th>Localização</th><th>Avaliação</th><th>Ações</th></tr></thead><tbody>';

    dadosEstabelecimentos.forEach(est => {
        html += `
            <tr>
                <td>${est.id}</td>
                <td>${est.titulo}</td>
                <td><span class="badge badge-categoria">${est.categoria}</span></td>
                <td>${est.localizacao}</td>
                <td>⭐ ${est.avaliacao.toFixed(1)}</td>
                <td>
                    <div class="acoes-tabela">
                        <button class="botao-editar" onclick="abrirModalEstabelecimento(${est.id})">Editar</button>
                        <button class="botao-deletar" onclick="confirmarDeletarEstabelecimento(${est.id})">Deletar</button>
                    </div>
                </td>
            </tr>
        `;
    });

    html += '</tbody></table>';
    listaEstabelecimentos.innerHTML = html;
}

function abrirModalEstabelecimento(id = null) {
    tituloModal.textContent = id ? 'Editar Estabelecimento' : 'Novo Estabelecimento';

    const categorias = ['comercios', 'servicos', 'profissionais', 'instituicoes'];
    let categoriasHtml = categorias.map(cat => `<option value="${cat}">${cat}</option>`).join('');

    let formularioHtml = `
        <div class="grupo-formulario-modal">
            <label>Título *</label>
            <input type="text" id="entradaTitulo" required>
        </div>
        <div class="grupo-formulario-modal">
            <label>Categoria *</label>
            <select id="entradaCategoria" required>
                <option value="">Selecione uma categoria</option>
                ${categoriasHtml}
            </select>
        </div>
        <div class="grupo-formulario-modal">
            <label>Descrição</label>
            <textarea id="entradaDescricao"></textarea>
        </div>
        <div class="grupo-formulario-modal">
            <label>Localização</label>
            <input type="text" id="entradaLocalizacao">
        </div>
        <div class="grupo-formulario-modal">
            <label>Avaliação</label>
            <input type="number" id="entradaAvaliacao" min="0" max="5" step="0.1" value="5">
        </div>
        <div class="botoes-modal">
            <button type="button" class="botao-cancelar" onclick="fecharModal()">Cancelar</button>
            <button type="button" class="botao-enviar" onclick="salvarEstabelecimento(${id})">Salvar</button>
        </div>
    `;

    formularioModal.innerHTML = formularioHtml;

    if (id) {
        const est = dadosEstabelecimentos.find(e => e.id === id);
        if (est) {
            document.getElementById('entradaTitulo').value = est.titulo;
            document.getElementById('entradaCategoria').value = est.categoria;
            document.getElementById('entradaDescricao').value = est.descricao;
            document.getElementById('entradaLocalizacao').value = est.localizacao;
            document.getElementById('entradaAvaliacao').value = est.avaliacao;
        }
    }

    modalFormulario.classList.add('ativo');
}

async function salvarEstabelecimento(id = null) {
    const titulo = document.getElementById('entradaTitulo').value;
    const categoria = document.getElementById('entradaCategoria').value;
    const descricao = document.getElementById('entradaDescricao').value;
    const localizacao = document.getElementById('entradaLocalizacao').value;
    const avaliacao = parseFloat(document.getElementById('entradaAvaliacao').value);

    const dados = {
        titulo: titulo,
        categoria: categoria,
        descricao: descricao,
        localizacao: localizacao,
        avaliacao: avaliacao
    };

    try {
        let resposta;
        if (id) {
            resposta = await fetch(`/api/admin/estabelecimentos/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(dados)
            });
        } else {
            resposta = await fetch('/api/admin/estabelecimentos', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(dados)
            });
        }

        const resultado = await resposta.json();
        if (resultado.sucesso) {
            fecharModal();
            carregarEstabelecimentos();
        }
    } catch (erro) {
        console.error('Erro ao salvar:', erro);
    }
}

function confirmarDeletarEstabelecimento(id) {
    itemSelecionadoParaDeletar = id;
    tipoItemSelecionado = 'estabelecimento';
    document.getElementById('textoConfirmacao').textContent = 'Tem certeza que deseja deletar este estabelecimento?';
    modalConfirmacao.classList.add('ativo');
}


async function carregarPrestadores() {
    try {
        const resposta = await fetch('/api/admin/prestadores');
        dadosPrestadores = await resposta.json();
        renderizarPrestadores();
    } catch (erro) {
        console.error('Erro ao carregar prestadores:', erro);
    }
}

function renderizarPrestadores() {
    const listaPrestadores = document.getElementById('listaPrestadores');

    if (dadosPrestadores.length === 0) {
        listaPrestadores.innerHTML = `
            <div class="cartao-vazio">
                <div class="icone">👨‍💼</div>
                <p>Nenhum prestador cadastrado</p>
            </div>
        `;
        return;
    }

    let html = '<table class="tabela"><thead><tr><th>ID</th><th>Nome</th><th>Profissão</th><th>Localização</th><th>Telefone</th><th>Status</th><th>Ações</th></tr></thead><tbody>';

    dadosPrestadores.forEach(prest => {
        const statusBadge = prest.verificado ? 
            '<span class="badge badge-verificado">✓ Verificado</span>' : 
            '<span class="badge badge-nao-verificado">✗ Não Verificado</span>';

        html += `
            <tr>
                <td>${prest.id}</td>
                <td>${prest.nome}</td>
                <td>${prest.profissao}</td>
                <td>${prest.localizacao}</td>
                <td>${prest.telefone}</td>
                <td>${statusBadge}</td>
                <td>
                    <div class="acoes-tabela">
                        <button class="botao-editar" onclick="abrirModalPrestador(${prest.id})">Editar</button>
                        <button class="botao-deletar" onclick="confirmarDeletarPrestador(${prest.id})">Deletar</button>
                    </div>
                </td>
            </tr>
        `;
    });

    html += '</tbody></table>';
    listaPrestadores.innerHTML = html;
}

function abrirModalPrestador(id = null) {
    tituloModal.textContent = id ? 'Editar Prestador' : 'Novo Prestador';

    let formularioHtml = `
        <div class="grupo-formulario-modal">
            <label>Nome *</label>
            <input type="text" id="entradaNome" required>
        </div>
        <div class="grupo-formulario-modal">
            <label>Profissão *</label>
            <input type="text" id="entradaProfissao" required>
        </div>
        <div class="grupo-formulario-modal">
            <label>Especialidades</label>
            <input type="text" id="entradaEspecialidade" placeholder="Digite e clique em Adicionar">
            <button type="button" class="botao-adicionar" onclick="adicionarEspecialidade()">Adicionar</button>
            <div id="listaEspecialidades" class="campo-especialidades" style="margin-top: 10px;"></div>
        </div>
        <div class="grupo-formulario-modal">
            <label>Localização</label>
            <input type="text" id="entradaLocalizacaoPrestador">
        </div>
        <div class="grupo-formulario-modal">
            <label>Telefone</label>
            <input type="text" id="entradaTelefonePrestador">
        </div>
        <div class="grupo-formulario-modal">
            <label>Descrição</label>
            <textarea id="entradaDescricaoPrestador"></textarea>
        </div>
        <div class="grupo-formulario-modal">
            <label>Avaliação</label>
            <input type="number" id="entradaAvaliacaoPrestador" min="0" max="5" step="0.1" value="5">
        </div>
        <div class="grupo-formulario-modal checkbox-verificado">
            <input type="checkbox" id="entradaVerificado">
            <label for="entradaVerificado" style="margin: 0;">Verificado</label>
        </div>
        <div class="botoes-modal">
            <button type="button" class="botao-cancelar" onclick="fecharModal()">Cancelar</button>
            <button type="button" class="botao-enviar" onclick="salvarPrestador(${id})">Salvar</button>
        </div>
    `;

    formularioModal.innerHTML = formularioHtml;

    if (id) {
        const prest = dadosPrestadores.find(p => p.id === id);
        if (prest) {
            document.getElementById('entradaNome').value = prest.nome;
            document.getElementById('entradaProfissao').value = prest.profissao;
            document.getElementById('entradaLocalizacaoPrestador').value = prest.localizacao;
            document.getElementById('entradaTelefonePrestador').value = prest.telefone;
            document.getElementById('entradaDescricaoPrestador').value = prest.descricao;
            document.getElementById('entradaAvaliacaoPrestador').value = prest.avaliacao;
            document.getElementById('entradaVerificado').checked = prest.verificado;

            const listaEspec = document.getElementById('listaEspecialidades');
            listaEspec.innerHTML = '';
            prest.especialidades.forEach((esp, idx) => {
                listaEspec.innerHTML += `
                    <div class="tag-especialidade">
                        ${esp}
                        <button type="button" onclick="removerEspecialidade(${idx})">×</button>
                    </div>
                `;
            });
        }
    }

    modalFormulario.classList.add('ativo');
}

let especialidadesTemporarias = [];

function adicionarEspecialidade() {
    const entrada = document.getElementById('entradaEspecialidade');
    const espec = entrada.value.trim();

    if (espec) {
        especialidadesTemporarias.push(espec);
        entrada.value = '';
        atualizarListaEspecialidades();
    }
}

function removerEspecialidade(idx) {
    especialidadesTemporarias.splice(idx, 1);
    atualizarListaEspecialidades();
}

function atualizarListaEspecialidades() {
    const listaEspec = document.getElementById('listaEspecialidades');
    listaEspec.innerHTML = '';
    especialidadesTemporarias.forEach((esp, idx) => {
        listaEspec.innerHTML += `
            <div class="tag-especialidade">
                ${esp}
                <button type="button" onclick="removerEspecialidade(${idx})">×</button>
            </div>
        `;
    });
}

async function salvarPrestador(id = null) {
    const nome = document.getElementById('entradaNome').value;
    const profissao = document.getElementById('entradaProfissao').value;
    const localizacao = document.getElementById('entradaLocalizacaoPrestador').value;
    const telefone = document.getElementById('entradaTelefonePrestador').value;
    const descricao = document.getElementById('entradaDescricaoPrestador').value;
    const avaliacao = parseFloat(document.getElementById('entradaAvaliacaoPrestador').value);
    const verificado = document.getElementById('entradaVerificado').checked;

    const dados = {
        nome: nome,
        profissao: profissao,
        especialidades: especialidadesTemporarias,
        localizacao: localizacao,
        telefone: telefone,
        descricao: descricao,
        avaliacao: avaliacao,
        verificado: verificado
    };

    try {
        let resposta;
        if (id) {
            resposta = await fetch(`/api/admin/prestadores/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(dados)
            });
        } else {
            resposta = await fetch('/api/admin/prestadores', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(dados)
            });
        }

        const resultado = await resposta.json();
        if (resultado.sucesso) {
            especialidadesTemporarias = [];
            fecharModal();
            carregarPrestadores();
        }
    } catch (erro) {
        console.error('Erro ao salvar:', erro);
    }
}

function confirmarDeletarPrestador(id) {
    itemSelecionadoParaDeletar = id;
    tipoItemSelecionado = 'prestador';
    document.getElementById('textoConfirmacao').textContent = 'Tem certeza que deseja deletar este prestador?';
    modalConfirmacao.classList.add('ativo');
}

async function carregarMensagens() {
    try {
        const resposta = await fetch('/api/admin/mensagens');
        dadosMensagens = await resposta.json();
        renderizarMensagens();
    } catch (erro) {
        console.error('Erro ao carregar mensagens:', erro);
    }
}

function renderizarMensagens() {
    const listaMensagens = document.getElementById('listaMensagens');

    if (dadosMensagens.length === 0) {
        listaMensagens.innerHTML = `
            <div class="cartao-vazio">
                <div class="icone">💬</div>
                <p>Nenhuma mensagem recebida</p>
            </div>
        `;
        return;
    }

    let html = '';

    dadosMensagens.forEach((msg, idx) => {
        const data = new Date(msg.criado_em).toLocaleDateString('pt-BR');
        html += `
            <div class="info-mensagem">
                <div class="dados-mensagem">
                    <div class="remetente">${msg.nome}</div>
                    <div class="assunto-mensagem"><strong>Assunto:</strong> ${msg.assunto}</div>
                    <div style="margin-bottom: 8px;"><strong>Mensagem:</strong> ${msg.mensagem}</div>
                    <div style="margin-bottom: 8px;"><strong>Email:</strong> ${msg.email}</div>
                    ${msg.telefone ? `<div style="margin-bottom: 8px;"><strong>Telefone:</strong> ${msg.telefone}</div>` : ''}
                    <div class="data-mensagem">Recebida em: ${data}</div>
                </div>
                <div style="display:flex;gap:8px;align-items:center;">
                    <button class="botao-responder" onclick="abrirModalResposta(${msg.id}, ${idx})" style="background:#3498db;color:#fff;padding:8px 12px;border-radius:4px;border:none;cursor:pointer;">Responder</button>
                    <button class="botao-deletar" onclick="confirmarDeletarMensagem(${msg.id})">Deletar</button>
                </div>
            </div>
        `;
    });

    listaMensagens.innerHTML = html;
}

function confirmarDeletarMensagem(idx) {
    itemSelecionadoParaDeletar = idx;
    tipoItemSelecionado = 'mensagem';
    document.getElementById('textoConfirmacao').textContent = 'Tem certeza que deseja deletar esta mensagem?';
    modalConfirmacao.classList.add('ativo');
}

function abrirModalResposta(msgId, idx) {
    const msg = dadosMensagens.find(m => m.id === msgId) || dadosMensagens[idx];
    const info = document.getElementById('resp-info');
    if (info && msg) {
        info.innerHTML = `<p><strong>De:</strong> ${msg.nome} &nbsp; &nbsp; <strong>Email:</strong> ${msg.email}</p><p><strong>Assunto:</strong> ${msg.assunto}</p>`;
    }
    document.getElementById('resp-texto').value = '';
    document.getElementById('modalResponder').dataset.msgId = msgId;
    document.getElementById('modalResponder').classList.add('ativo');
}

function fecharModalResponder() {
    document.getElementById('modalResponder').classList.remove('ativo');
    document.getElementById('modalResponder').dataset.msgId = '';
}

async function enviarRespostaModal() {
    const modal = document.getElementById('modalResponder');
    const msgId = modal.dataset.msgId;
    const texto = document.getElementById('resp-texto').value.trim();
    if (!texto || texto.length < 5) {
        alert('A resposta deve ter pelo menos 5 caracteres');
        return;
    }
    try {
        const resp = await fetch(`/api/admin/mensagens/${msgId}/responder`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ resposta: texto })
        });
        const resultado = await resp.json();
        if (resp.ok || resultado.sucesso) {
            alert('✅ Resposta enviada com sucesso!');
            fecharModalResponder();
            carregarMensagens();
        } else {
            alert('Erro: ' + (resultado.erro || 'Não foi possível enviar a resposta'));
        }
    } catch (e) {
        console.error('Erro ao enviar resposta:', e);
        alert('Erro ao enviar resposta');
    }
}

function fecharModal() {
    modalFormulario.classList.remove('ativo');
    especialidadesTemporarias = [];
}

function fecharModalConfirmacao() {
    modalConfirmacao.classList.remove('ativo');
    itemSelecionadoParaDeletar = null;
    tipoItemSelecionado = null;
}

