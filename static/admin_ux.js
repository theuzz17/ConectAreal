console.log('admin_ux.js loaded');

document.addEventListener('DOMContentLoaded', function() {
    // Legacy admin panel: trocar seções via sidebar
    document.querySelectorAll('.item-menu').forEach(function(el){
        el.addEventListener('click', function(e){
            e.preventDefault();
            document.querySelectorAll('.item-menu').forEach(i=>i.classList.remove('ativo'));
            this.classList.add('ativo');
            const secao = this.getAttribute('data-secao');
            if(!secao) return;
            document.querySelectorAll('.secao-conteudo').forEach(s=>s.classList.remove('ativa'));
            const target = document.getElementById(secao);
            if(target) target.classList.add('ativa');
            const titulo = {estabelecimentos: 'Gerenciar Estabelecimentos', prestadores: 'Gerenciar Prestadores', mensagens: 'Mensagens'}[secao];
            const tituloEl = document.getElementById('titulo-pagina');
            if(tituloEl && titulo) tituloEl.textContent = titulo;
        });
    });

    // Novo painel: toggle sidebar e navegação
    const toggle = document.getElementById('toggle-menu');
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('main-content');
    if(toggle && sidebar && mainContent){
        toggle.addEventListener('click', function(){
            sidebar.classList.toggle('ativo');
            mainContent.classList.toggle('deslocado');
        });
    }

    // Navegação do novo painel entre seções
    document.querySelectorAll('.menu-link').forEach(function(link){
        link.addEventListener('click', function(e){
            e.preventDefault();
            document.querySelectorAll('.menu-link').forEach(l=>l.classList.remove('ativo'));
            this.classList.add('ativo');
            const sec = this.getAttribute('data-secao');
            if(!sec) return;
            document.querySelectorAll('[id]').forEach(el=>{
                if(el.id === sec) el.style.display = '';
                else if(el.classList.contains('secao-ativa') || el.style.display === '') el.style.display = 'none';
            });
            const target = document.getElementById(sec);
            if(target){ target.style.display = ''; window.scrollTo({top:0,behavior:'smooth'}); }
        });
    });

    // Fechar modais com ESC
    document.addEventListener('keydown', function(e){
        if(e.key === 'Escape'){
            document.querySelectorAll('.modal.ativo').forEach(m=>m.classList.remove('ativo'));
        }
    });

    // Micro-feedback: adicionar efeito leve em botões quando clicados
    document.querySelectorAll('button').forEach(function(btn){
        btn.addEventListener('mousedown', function(){ btn.style.transform = 'scale(0.98)'; });
        btn.addEventListener('mouseup', function(){ btn.style.transform = ''; });
        btn.addEventListener('mouseleave', function(){ btn.style.transform = ''; });
    });
});

// Pequena função utilitária para mostrar um alerta temporário (novo painel)
function showToast(message, kind='info', timeout=3000){
    const container = document.getElementById('alertas-container');
    if(!container) return;
    const el = document.createElement('div');
    el.className = 'alerta alerta-' + (kind==='error' ? 'erro' : (kind==='success' ? 'sucesso' : 'info'));
    el.textContent = message;
    container.appendChild(el);
    setTimeout(()=>{ el.style.opacity = '0'; setTimeout(()=>el.remove(),400); }, timeout);
}

export { showToast };
