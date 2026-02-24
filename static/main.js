document.addEventListener('DOMContentLoaded', function() {
    const alternarBarraNavegacao = document.getElementById('alternadorBarraNavegacao');
    const menuBarraNavegacao = document.getElementById('menuBarraNavegacao');
    if (alternarBarraNavegacao && menuBarraNavegacao) {
        alternarBarraNavegacao.addEventListener('click', function() {
            alternarBarraNavegacao.classList.toggle('active');
            menuBarraNavegacao.classList.toggle('active');
        });

        const linksNavegacao = menuBarraNavegacao.querySelectorAll('.link-navegacao');
        linksNavegacao.forEach(link => {
            link.addEventListener('click', function() {
                alternarBarraNavegacao.classList.remove('active');
                menuBarraNavegacao.classList.remove('active');
            });
        });
    }

    carregarEstabelecimentos();
    carregarPrestadores();

    configurarFiltros();
    configurarFormularioContato();
    configurarRolagemBarraNavegacao();
    iniciarObservadorAnimacao();
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href !== '#' && document.querySelector(href)) {
                e.preventDefault();
                document.querySelector(href).scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
});

function carregarEstabelecimentos(filtro = 'todos', termoBusca = '') {
    const url = new URL('/api/estabelecimentos', window.location.origin);
    url.searchParams.append('filtro', filtro);
    url.searchParams.append('busca', termoBusca);

    fetch(url)
        .then(response => response.json())
        .then(data => renderizarEstabelecimentos(data))
        .catch(error => console.error('Erro ao carregar estabelecimentos:', error));
}

function renderizarEstabelecimentos(estabelecimentos) {
    const gradeEstabelecimentos = document.getElementById('gradeServicos');
    
    gradeEstabelecimentos.innerHTML = estabelecimentos.map(estabelecimento => `
        <div class="cartao-servico">
            <div class="cabecalho-servico">
                <div>
                    <div class="titulo-servico">${estabelecimento.titulo}</div>
                    <div class="categoria-servico">${estabelecimento.categoria}</div>
                </div>
                <div class="avaliacao-servico">⭐ ${estabelecimento.avaliacao}</div>
            </div>
            <p class="descricao-servico">${estabelecimento.descricao}</p>
            <div class="informacao-servico">
                <span>📍 ${estabelecimento.localizacao}</span>
            </div>
            <div class="rodape-servico">
                <span class="avaliacoes-servico">${estabelecimento.avaliacoes} avaliações</span>
                <button class="btn btn-primario" onclick="alert('Detalhes do estabelecimento: ${estabelecimento.titulo}')">Ver Detalhes</button>
            </div>
        </div>
    `).join('');
}

function carregarPrestadores() {
    fetch('/api/prestadores')
        .then(response => response.json())
        .then(data => renderizarPrestadores(data))
        .catch(error => console.error('Erro ao carregar prestadores:', error));
}

function renderizarPrestadores(prestadores) {
    const gradePrestadores = document.getElementById('gradePrestadores');
    
    gradePrestadores.innerHTML = prestadores.map(prestador => `
        <div class="cartao-profissional">
            <div class="cabecalho-profissional">
                <div class="nome-profissional">${prestador.nome} ${prestador.verificado ? '✓' : ''}</div>
                <div class="titulo-profissional">${prestador.profissao}</div>
            </div>
            <div class="corpo-profissional">
                <p class="descricao-profissional">${prestador.descricao}</p>
                <div class="especialidades-profissional">
                    ${prestador.especialidades.map(especialidade => `<span class="emblema-especialidade">${especialidade}</span>`).join('')}
                </div>
                <div class="informacoes-profissional">
                    <div class="item-informacao">⭐ ${prestador.avaliacao} (${prestador.avaliacoes} avaliações)</div>
                    <div class="item-informacao">📍 ${prestador.localizacao}</div>
                    <div class="item-informacao">📞 ${prestador.telefone}</div>
                </div>
                <div class="acoes-profissional">
                    <button class="btn btn-primario" onclick="alert('Ligando para ${prestador.nome}...')">Ligar</button>
                    <button class="btn btn-contorno" onclick="alert('Enviando mensagem para ${prestador.nome}...')">Mensagem</button>
                </div>
            </div>
        </div>
    `).join('');
}

function configurarFiltros() {
    const abasFiltro = document.querySelectorAll('.aba-filtro');
    const entradaBusca = document.getElementById('entradaBusca');

    abasFiltro.forEach(aba => {
        aba.addEventListener('click', function() {
            abasFiltro.forEach(a => a.classList.remove('ativo'));
            this.classList.add('ativo');
            
            const filtro = this.getAttribute('data-filter');
            const termoBusca = entradaBusca.value;
            carregarEstabelecimentos(filtro, termoBusca);
        });
    });

    entradaBusca.addEventListener('input', function() {
        const filtroAtivo = document.querySelector('.aba-filtro.ativo').getAttribute('data-filter');
        carregarEstabelecimentos(filtroAtivo, this.value);
    });
}

function configurarFormularioContato() {
    const formularioContato = document.getElementById('formularioContato');
    
    formularioContato.addEventListener('submit', function(e) {
        e.preventDefault();
        const nome = document.getElementById('nome').value.trim();
        const email = document.getElementById('email').value.trim();
        const telefoneBruto = document.getElementById('telefone').value;
        const telefoneNumeros = telefoneBruto.replace(/\D/g, '');
        const assunto = document.getElementById('assunto').value;
        const mensagem = document.getElementById('mensagem').value.trim();

        const botaoEnviar = formularioContato.querySelector('button[type="submit"]');
        const textoOriginal = botaoEnviar.textContent;
        const erroEmailEl = document.getElementById('erroEmail');
        const erroTelefoneEl = document.getElementById('erroTelefone');
        const mensagemFormularioEl = document.getElementById('mensagemFormulario');

        function limparMensagens() {
            if (erroEmailEl) erroEmailEl.textContent = '';
            if (erroTelefoneEl) erroTelefoneEl.textContent = '';
            if (mensagemFormularioEl) {
                mensagemFormularioEl.textContent = '';
                mensagemFormularioEl.className = 'form-mensagem';
            }
        }

        limparMensagens();

        const emailValido = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
        if (!emailValido) {
            if (erroEmailEl) erroEmailEl.textContent = 'Por favor, informe um email válido.';
            if (document.getElementById('email')) document.getElementById('email').focus();
            return;
        }

        if (telefoneNumeros.length > 0 && telefoneNumeros.length !== 11) {
            if (erroTelefoneEl) erroTelefoneEl.textContent = 'Por favor, informe um telefone com exatamente 11 dígitos (somente números).';
            if (document.getElementById('telefone')) document.getElementById('telefone').focus();
            return;
        }

        botaoEnviar.textContent = '⏳ Enviando...';
        botaoEnviar.disabled = true;

        fetch('/api/contato', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                nome: nome,
                email: email,
                telefone: telefoneBruto,
                assunto: assunto,
                mensagem: mensagem
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.sucesso) {
                if (mensagemFormularioEl) {
                    mensagemFormularioEl.textContent = data.mensagem;
                    mensagemFormularioEl.classList.add('sucesso');
                } else {
                    alert(data.mensagem);
                }
                formularioContato.reset();
            } else {
                if (erroEmailEl && data.erro.includes('email')) {
                    erroEmailEl.textContent = data.erro;
                } else if (erroTelefoneEl && data.erro.includes('telefone')) {
                    erroTelefoneEl.textContent = data.erro;
                } else {
                    alert(data.erro || 'Erro ao enviar mensagem.');
                }
            }
            botaoEnviar.textContent = textoOriginal;
            botaoEnviar.disabled = false;
        })
        .catch(error => {
            console.error('Erro:', error);
            alert('Erro ao enviar mensagem. Tente novamente.');
            botaoEnviar.textContent = textoOriginal;
            botaoEnviar.disabled = false;
        });
    });

    const emailInput = document.getElementById('email');
    const telefoneInput = document.getElementById('telefone');
    if (emailInput) emailInput.addEventListener('input', () => {
        const erroEmailEl = document.getElementById('erroEmail'); 
        if (erroEmailEl) erroEmailEl.textContent = '';
    });
    if (telefoneInput) telefoneInput.addEventListener('input', () => {
        const erroTelefoneEl = document.getElementById('erroTelefone'); 
        if (erroTelefoneEl) erroTelefoneEl.textContent = '';
    });
}

function configurarRolagemBarraNavegacao() {
    const barraNavegacao = document.getElementById('barraNavegacao');

    window.addEventListener('scroll', () => {
        const rolagemAtual = window.pageYOffset;
        
        if (rolagemAtual > 100) {
            barraNavegacao.style.boxShadow = '0 4px 16px rgba(0, 0, 0, 0.12)';
        } else {
            barraNavegacao.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.08)';
        }
    });
}

function iniciarObservadorAnimacao() {
    const opcoesObservador = {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px'
    };

    const observador = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observador.unobserve(entry.target);
            }
        });
    }, opcoesObservador);

    const cards = document.querySelectorAll('.cartao-servico, .cartao-profissional, .cartao-recurso');
    cards.forEach(card => {
        observador.observe(card);
    });
    
    addAnimacaoRolagem();
}

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const href = this.getAttribute('href');
        if (href !== '#' && document.querySelector(href)) {
            e.preventDefault();
            document.querySelector(href).scrollIntoView({
                behavior: 'smooth'
            });
        }
    });
});

function addAnimacaoRolagem() {
    const elementos = document.querySelectorAll('.cartao-servico, .cartao-profissional');
    
    const observador = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'slideInUp 0.6s ease-out forwards';
                observador.unobserve(entry.target);
            }
        });
    });
    
    elementos.forEach(el => observador.observe(el));
}
