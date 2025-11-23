const estabelecimentos = [
    {
        id: 1,
        titulo: "Encanador Profissional",
        categoria: "profissionais",
        descricao: "Serviços de encanamento residencial e comercial com garantia",
        avaliacao: 4.8,
        avaliacoes: 24,
        localizacao: "Centro do Bairro"
    },
    {
        id: 2,
        titulo: "Padaria Artesanal",
        categoria: "comercios",
        descricao: "Pães frescos e bolos caseiros todos os dias",
        avaliacao: 4.9,
        avaliacoes: 45,
        localizacao: "Rua Principal"
    },
    {
        id: 3,
        titulo: "Aulas de Reforço Escolar",
        categoria: "servicos",
        descricao: "Reforço em matemática, português e inglês para crianças",
        avaliacao: 4.7,
        avaliacoes: 18,
        localizacao: "Próximo à Escola"
    },
    {
        id: 4,
        titulo: "Clínica de Saúde",
        categoria: "instituicoes",
        descricao: "Atendimento médico geral e especializado com agendamento",
        avaliacao: 4.6,
        avaliacoes: 52,
        localizacao: "Avenida Central"
    },
    {
        id: 5,
        titulo: "Salão de Beleza",
        categoria: "comercios",
        descricao: "Cabelo, manicure, pedicure e estética facial",
        avaliacao: 4.8,
        avaliacoes: 36,
        localizacao: "Rua das Flores"
    },
    {
        id: 6,
        titulo: "Aulas de Yoga",
        categoria: "servicos",
        descricao: "Bem-estar e equilíbrio corpo e mente para todas as idades",
        avaliacao: 4.9,
        avaliacoes: 28,
        localizacao: "Parque do Bairro"
    },
    {
        id: 7,
        titulo: "Eletricista",
        categoria: "profissionais",
        descricao: "Instalações elétricas e manutenção com segurança",
        avaliacao: 4.7,
        avaliacoes: 31,
        localizacao: "Zona Residencial"
    },
    {
        id: 8,
        titulo: "Supermercado Local",
        categoria: "comercios",
        descricao: "Alimentos frescos, bebidas e produtos de limpeza",
        avaliacao: 4.5,
        avaliacoes: 67,
        localizacao: "Avenida Principal"
    },
    {
        id: 9,
        titulo: "Consultório Odontológico",
        categoria: "instituicoes",
        descricao: "Limpeza, restauração e tratamentos dentários",
        avaliacao: 4.8,
        avaliacoes: 43,
        localizacao: "Centro"
    },
    {
        id: 10,
        titulo: "Aulas de Inglês",
        categoria: "servicos",
        descricao: "Inglês para crianças, adolescentes e adultos",
        avaliacao: 4.6,
        avaliacoes: 22,
        localizacao: "Centro Educacional"
    }
];

const prestadores = [
    {
        id: 1,
        nome: "João Silva",
        profissao: "Encanador",
        especialidades: ["Encanamento", "Hidráulica", "Manutenção"],
        avaliacao: 4.8,
        avaliacoes: 24,
        localizacao: "Centro do Bairro",
        telefone: "(11) 98765-4321",
        descricao: "Profissional experiente em serviços de encanamento residencial e comercial com garantia de qualidade.",
        verificado: true
    },
    {
        id: 2,
        nome: "Maria Santos",
        profissao: "Eletricista",
        especialidades: ["Instalações", "Manutenção", "Projetos"],
        avaliacao: 4.7,
        avaliacoes: 31,
        localizacao: "Zona Residencial",
        telefone: "(11) 5555-6666",
        descricao: "Eletricista certificada com experiência em instalações elétricas seguras e eficientes.",
        verificado: true
    },
    {
        id: 3,
        nome: "Carlos Oliveira",
        profissao: "Pintor",
        especialidades: ["Pintura Residencial", "Pintura Comercial", "Restauração"],
        avaliacao: 4.6,
        avaliacoes: 18,
        localizacao: "Bairro Central",
        telefone: "(11) 7777-8888",
        descricao: "Pintor profissional especializado em acabamentos de qualidade e cores personalizadas.",
        verificado: false
    },
    {
        id: 4,
        nome: "Ana Costa",
        profissao: "Personal Trainer",
        especialidades: ["Musculação", "Cardio", "Treinamento Funcional"],
        avaliacao: 4.9,
        avaliacoes: 42,
        localizacao: "Parque do Bairro",
        telefone: "(11) 9999-0000",
        descricao: "Personal trainer certificada com foco em resultados e bem-estar do cliente.",
        verificado: true
    },
    {
        id: 5,
        nome: "Roberto Ferreira",
        profissao: "Carpinteiro",
        especialidades: ["Móveis", "Reformas", "Acabamentos"],
        avaliacao: 4.5,
        avaliacoes: 22,
        localizacao: "Rua Principal",
        telefone: "(11) 4444-5555",
        descricao: "Carpinteiro experiente em projetos personalizados e acabamentos refinados.",
        verificado: true
    },
    {
        id: 6,
        nome: "Fernanda Lima",
        profissao: "Professora Particular",
        especialidades: ["Matemática", "Português", "Inglês"],
        avaliacao: 4.8,
        avaliacoes: 28,
        localizacao: "Centro Educacional",
        telefone: "(11) 3333-4444",
        descricao: "Professora dedicada com metodologia comprovada para melhoria de desempenho escolar.",
        verificado: true
    }
];

document.addEventListener('DOMContentLoaded', function() {
    const alternarBarraNavegacao = document.getElementById('alternadorBarraNavegacao');
    const menuBarraNavegacao = document.getElementById('menuBarraNavegacao');

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

    renderizarEstabelecimentos();
    renderizarPrestadores();

    configurarFiltros();
    configurarFormularioContato();
    configurarRolagemBarraNavegacao();
    iniciarObservadorAnimacao();
});

function renderizarEstabelecimentos(filtro = 'todos', termoBusca = '') {
    const gradeEstabelecimentos = document.getElementById('gradeServicos');
    
    let filtrados = estabelecimentos.filter(estabelecimento => {
        const correspondeFiltro = filtro === 'todos' || estabelecimento.categoria === filtro;
        const correspondeBusca = termoBusca === '' || 
            estabelecimento.titulo.toLowerCase().includes(termoBusca.toLowerCase()) ||
            estabelecimento.descricao.toLowerCase().includes(termoBusca.toLowerCase());
        return correspondeFiltro && correspondeBusca;
    });

    gradeEstabelecimentos.innerHTML = filtrados.map(estabelecimento => `
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

function renderizarPrestadores() {
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
            renderizarEstabelecimentos(filtro, termoBusca);
        });
    });

    entradaBusca.addEventListener('input', function() {
        const filtroAtivo = document.querySelector('.aba-filtro.ativo').getAttribute('data-filter');
        renderizarEstabelecimentos(filtroAtivo, this.value);
    });
}

function configurarFormularioContato() {
    const formularioContato = document.getElementById('formularioContato');
    
    formularioContato.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const nome = document.getElementById('name').value;
        const botaoEnviar = formularioContato.querySelector('button[type="submit"]');
        const textoOriginal = botaoEnviar.textContent;
        
        botaoEnviar.textContent = '⏳ Enviando...';
        botaoEnviar.disabled = true;
        
        setTimeout(() => {
            alert(`Obrigado ${nome}! Sua mensagem foi enviada com sucesso. Responderemos em breve!`);
            formularioContato.reset();
            botaoEnviar.textContent = textoOriginal;
            botaoEnviar.disabled = false;
        }, 1500);
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