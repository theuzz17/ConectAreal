// ============================================
// DADOS DO SITE
// ============================================

const services = [
    {
        id: 1,
        title: "Encanador Profissional",
        category: "profissionais",
        description: "Serviços de encanamento residencial e comercial com garantia",
        rating: 4.8,
        reviews: 24,
        location: "Centro do Bairro"
    },
    {
        id: 2,
        title: "Padaria Artesanal",
        category: "comercios",
        description: "Pães frescos e bolos caseiros todos os dias",
        rating: 4.9,
        reviews: 45,
        location: "Rua Principal"
    },
    {
        id: 3,
        title: "Aulas de Reforço Escolar",
        category: "servicos",
        description: "Reforço em matemática, português e inglês para crianças",
        rating: 4.7,
        reviews: 18,
        location: "Próximo à Escola"
    },
    {
        id: 4,
        title: "Clínica de Saúde",
        category: "instituicoes",
        description: "Atendimento médico geral e especializado com agendamento",
        rating: 4.6,
        reviews: 52,
        location: "Avenida Central"
    },
    {
        id: 5,
        title: "Salão de Beleza",
        category: "comercios",
        description: "Cabelo, manicure, pedicure e estética facial",
        rating: 4.8,
        reviews: 36,
        location: "Rua das Flores"
    },
    {
        id: 6,
        title: "Aulas de Yoga",
        category: "servicos",
        description: "Bem-estar e equilíbrio corpo e mente para todas as idades",
        rating: 4.9,
        reviews: 28,
        location: "Parque do Bairro"
    },
    {
        id: 7,
        title: "Eletricista",
        category: "profissionais",
        description: "Instalações elétricas e manutenção com segurança",
        rating: 4.7,
        reviews: 31,
        location: "Zona Residencial"
    },
    {
        id: 8,
        title: "Supermercado Local",
        category: "comercios",
        description: "Alimentos frescos, bebidas e produtos de limpeza",
        rating: 4.5,
        reviews: 67,
        location: "Avenida Principal"
    },
    {
        id: 9,
        title: "Consultório Odontológico",
        category: "instituicoes",
        description: "Limpeza, restauração e tratamentos dentários",
        rating: 4.8,
        reviews: 43,
        location: "Centro"
    },
    {
        id: 10,
        title: "Aulas de Inglês",
        category: "servicos",
        description: "Inglês para crianças, adolescentes e adultos",
        rating: 4.6,
        reviews: 22,
        location: "Centro Educacional"
    }
];

const professionals = [
    {
        id: 1,
        name: "João Silva",
        profession: "Encanador",
        specialties: ["Encanamento", "Hidráulica", "Manutenção"],
        rating: 4.8,
        reviews: 24,
        location: "Centro do Bairro",
        phone: "(11) 98765-4321",
        description: "Profissional experiente em serviços de encanamento residencial e comercial com garantia de qualidade.",
        verified: true
    },
    {
        id: 2,
        name: "Maria Santos",
        profession: "Eletricista",
        specialties: ["Instalações", "Manutenção", "Projetos"],
        rating: 4.7,
        reviews: 31,
        location: "Zona Residencial",
        phone: "(11) 5555-6666",
        description: "Eletricista certificada com experiência em instalações elétricas seguras e eficientes.",
        verified: true
    },
    {
        id: 3,
        name: "Carlos Oliveira",
        profession: "Pintor",
        specialties: ["Pintura Residencial", "Pintura Comercial", "Restauração"],
        rating: 4.6,
        reviews: 18,
        location: "Bairro Central",
        phone: "(11) 7777-8888",
        description: "Pintor profissional especializado em acabamentos de qualidade e cores personalizadas.",
        verified: false
    },
    {
        id: 4,
        name: "Ana Costa",
        profession: "Personal Trainer",
        specialties: ["Musculação", "Cardio", "Treinamento Funcional"],
        rating: 4.9,
        reviews: 42,
        location: "Parque do Bairro",
        phone: "(11) 9999-0000",
        description: "Personal trainer certificada com foco em resultados e bem-estar do cliente.",
        verified: true
    },
    {
        id: 5,
        name: "Roberto Ferreira",
        profession: "Carpinteiro",
        specialties: ["Móveis", "Reformas", "Acabamentos"],
        rating: 4.5,
        reviews: 22,
        location: "Rua Principal",
        phone: "(11) 4444-5555",
        description: "Carpinteiro experiente em projetos personalizados e acabamentos refinados.",
        verified: true
    },
    {
        id: 6,
        name: "Fernanda Lima",
        profession: "Professora Particular",
        specialties: ["Matemática", "Português", "Inglês"],
        rating: 4.8,
        reviews: 28,
        location: "Centro Educacional",
        phone: "(11) 3333-4444",
        description: "Professora dedicada com metodologia comprovada para melhoria de desempenho escolar.",
        verified: true
    }
];

// ============================================
// NAVBAR TOGGLE
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    const navbarToggle = document.getElementById('navbarToggle');
    const navbarMenu = document.getElementById('navbarMenu');

    navbarToggle.addEventListener('click', function() {
        navbarToggle.classList.toggle('active');
        navbarMenu.classList.toggle('active');
    });

    // Fechar menu ao clicar em um link
    const navLinks = navbarMenu.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            navbarToggle.classList.remove('active');
            navbarMenu.classList.remove('active');
        });
    });

    // Renderizar serviços e profissionais
    renderServices();
    renderProfessionals();

    // Configurar filtros
    setupFilters();

    // Configurar formulário de contato
    setupContactForm();

    // Efeito de scroll na navbar
    setupNavbarScroll();
});

// ============================================
// RENDERIZAR SERVIÇOS
// ============================================

function renderServices(filter = 'todos', searchQuery = '') {
    const servicesGrid = document.getElementById('servicesGrid');
    
    let filtered = services.filter(service => {
        const matchesFilter = filter === 'todos' || service.category === filter;
        const matchesSearch = searchQuery === '' || 
            service.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
            service.description.toLowerCase().includes(searchQuery.toLowerCase());
        return matchesFilter && matchesSearch;
    });

    servicesGrid.innerHTML = filtered.map(service => `
        <div class="service-card">
            <div class="service-header">
                <div>
                    <div class="service-title">${service.title}</div>
                    <div class="service-category">${service.category}</div>
                </div>
                <div class="service-rating">⭐ ${service.rating}</div>
            </div>
            <p class="service-description">${service.description}</p>
            <div class="service-info">
                <span>📍 ${service.location}</span>
            </div>
            <div class="service-footer">
                <span class="service-reviews">${service.reviews} avaliações</span>
                <button class="btn btn-primary" onclick="alert('Detalhes do serviço: ${service.title}')">Ver Detalhes</button>
            </div>
        </div>
    `).join('');
}

// ============================================
// RENDERIZAR PROFISSIONAIS
// ============================================

function renderProfessionals() {
    const professionalsGrid = document.getElementById('professionalsGrid');
    
    professionalsGrid.innerHTML = professionals.map(prof => `
        <div class="professional-card">
            <div class="professional-header">
                <div class="professional-name">${prof.name} ${prof.verified ? '✓' : ''}</div>
                <div class="professional-title">${prof.profession}</div>
            </div>
            <div class="professional-body">
                <p class="professional-description">${prof.description}</p>
                <div class="professional-specialties">
                    ${prof.specialties.map(spec => `<span class="specialty-badge">${spec}</span>`).join('')}
                </div>
                <div class="professional-info">
                    <div class="info-item">⭐ ${prof.rating} (${prof.reviews} avaliações)</div>
                    <div class="info-item">📍 ${prof.location}</div>
                    <div class="info-item">📞 ${prof.phone}</div>
                </div>
                <div class="professional-actions">
                    <button class="btn btn-primary" onclick="alert('Ligando para ${prof.name}...')">Ligar</button>
                    <button class="btn btn-outline" onclick="alert('Enviando mensagem para ${prof.name}...')">Mensagem</button>
                </div>
            </div>
        </div>
    `).join('');
}

// ============================================
// CONFIGURAR FILTROS
// ============================================

function setupFilters() {
    const filterTabs = document.querySelectorAll('.filter-tab');
    const searchInput = document.getElementById('searchInput');

    filterTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            // Remover classe active de todos os tabs
            filterTabs.forEach(t => t.classList.remove('active'));
            // Adicionar classe active ao tab clicado
            this.classList.add('active');
            
            const filter = this.getAttribute('data-filter');
            const searchQuery = searchInput.value;
            renderServices(filter, searchQuery);
        });
    });

    // Busca em tempo real
    searchInput.addEventListener('input', function() {
        const activeFilter = document.querySelector('.filter-tab.active').getAttribute('data-filter');
        renderServices(activeFilter, this.value);
    });
}

// ============================================
// CONFIGURAR FORMULÁRIO DE CONTATO
// ============================================

function setupContactForm() {
    const contactForm = document.getElementById('contactForm');
    
    contactForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const name = document.getElementById('name').value;
        const email = document.getElementById('email').value;
        const subject = document.getElementById('subject').value;
        
        // Simular envio
        const submitBtn = contactForm.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        
        submitBtn.textContent = '⏳ Enviando...';
        submitBtn.disabled = true;
        
        setTimeout(() => {
            alert(`Obrigado ${name}! Sua mensagem foi enviada com sucesso. Responderemos em breve!`);
            contactForm.reset();
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        }, 1500);
    });
}

// ============================================
// EFEITO DE SCROLL NA NAVBAR
// ============================================

function setupNavbarScroll() {
    const navbar = document.getElementById('navbar');
    let lastScroll = 0;

    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;
        
        if (currentScroll > 100) {
            navbar.style.boxShadow = '0 4px 16px rgba(0, 0, 0, 0.12)';
        } else {
            navbar.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.08)';
        }
        
        lastScroll = currentScroll;
    });
}

// ============================================
// OBSERVADOR DE INTERSECÇÃO PARA ANIMAÇÕES
// ============================================

const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('fade-in');
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

// Observar cards quando a página carrega
document.addEventListener('DOMContentLoaded', function() {
    const cards = document.querySelectorAll('.service-card, .professional-card, .feature-card, .education-card');
    cards.forEach(card => {
        observer.observe(card);
    });
});

// ============================================
// FUNÇÕES UTILITÁRIAS
// ============================================

// Smooth scroll para links âncora
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

// Adicionar classe ao elemento quando entra em viewport
function addScrollAnimation() {
    const elements = document.querySelectorAll('.service-card, .professional-card');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'slideInUp 0.6s ease-out forwards';
                observer.unobserve(entry.target);
            }
        });
    });
    
    elements.forEach(el => observer.observe(el));
}

// Executar animação de scroll
window.addEventListener('load', addScrollAnimation);
