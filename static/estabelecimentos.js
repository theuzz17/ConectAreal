class GerenciadorEstabelecimentos {
    constructor() {
        this.paginaAtual = 1;
        this.totalPaginas = 1;
        this.inicializar();
    }

    inicializar() {
        this.carregarEstabelecimentos();
        document.getElementById('btn-criar-estab')?.addEventListener('click', () => {
            window.location.href = '/estabelecimentos/criar';
        });
    }

    carregarEstabelecimentos(pagina = 1) {
        const url = `/estabelecimentos/api/meus?pagina=${pagina}`;
        
        fetch(url)
            .then(response => response.json())
            .then(data => {
                if (data.sucesso) {
                    this.renderizarEstabelecimentos(data.estabelecimentos);
                    this.paginaAtual = data.pagina_atual;
                    this.totalPaginas = data.paginas;
                    this.renderizarPaginacao(data.pagina_atual, data.paginas);
                } else {
                    this.mostrarErro(data.erro);
                }
            })
            .catch(error => {
                console.error('Erro:', error);
                this.mostrarErro('Erro ao carregar estabelecimentos');
            });
    }

    renderizarEstabelecimentos(estabelecimentos) {
        const container = document.getElementById('estabelecimentos-container');
        
        if (estabelecimentos.length === 0) {
            container.innerHTML = `
                <div class="alert alert-info text-center">
                    <p>Você ainda não cadastrou nenhum estabelecimento.</p>
                    <p><a href="/estabelecimentos/criar" class="btn btn-primary">Cadastrar Agora</a></p>
                </div>
            `;
            return;
        }

        let html = '<div class="row">';
        
        estabelecimentos.forEach(estab => {
            html += `
                <div class="col-md-6 mb-4">
                    <div class="card h-100">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-start mb-3">
                                <h5 class="card-title mb-0">${estab.nome}</h5>
                                <span class="badge bg-${estab.ativo ? 'success' : 'danger'}">
                                    ${estab.ativo ? 'Ativo' : 'Inativo'}
                                </span>
                            </div>
                            
                            <p class="badge bg-info mb-2">${estab.categoria}</p>
                            
                            <p class="card-text text-muted small mb-3">${estab.descricao.substring(0, 100)}...</p>
                            
                            ${estab.verificado ? '<p class="badge bg-success mb-2"><i class="bi bi-check-circle"></i> Verificado</p>' : ''}
                            
                            <div class="mt-3 d-flex gap-2">
                                <a href="/estabelecimentos/${estab.id}" class="btn btn-sm btn-outline-primary" target="_blank">
                                    Ver
                                </a>
                                <a href="/estabelecimentos/editar/${estab.id}" class="btn btn-sm btn-warning">
                                    Editar
                                </a>
                                <button type="button" class="btn btn-sm btn-danger" onclick="gerenciadorEstab.deletar(${estab.id})">
                                    Deletar
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        container.innerHTML = html;
    }

    renderizarPaginacao(paginaAtual, totalPaginas) {
        const container = document.getElementById('paginacao-container');
        
        if (totalPaginas <= 1) {
            container.innerHTML = '';
            return;
        }

        let html = '<nav><ul class="pagination justify-content-center">';
        
        if (paginaAtual > 1) {
            html += `<li class="page-item"><a class="page-link" href="#" onclick="gerenciadorEstab.carregarEstabelecimentos(${paginaAtual - 1}); return false;">Anterior</a></li>`;
        }
        
        for (let i = 1; i <= totalPaginas; i++) {
            if (i === paginaAtual) {
                html += `<li class="page-item active"><span class="page-link">${i}</span></li>`;
            } else {
                html += `<li class="page-item"><a class="page-link" href="#" onclick="gerenciadorEstab.carregarEstabelecimentos(${i}); return false;">${i}</a></li>`;
            }
        }
        
        if (paginaAtual < totalPaginas) {
            html += `<li class="page-item"><a class="page-link" href="#" onclick="gerenciadorEstab.carregarEstabelecimentos(${paginaAtual + 1}); return false;">Próxima</a></li>`;
        }
        
        html += '</ul></nav>';
        container.innerHTML = html;
    }

    deletar(id) {
        if (confirm('Tem certeza que deseja deletar este estabelecimento? Esta ação não pode ser desfeita.')) {
            fetch(`/estabelecimentos/api/deletar/${id}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.sucesso) {
                    alert(data.mensagem);
                    this.carregarEstabelecimentos(this.paginaAtual);
                } else {
                    this.mostrarErro(data.erro);
                }
            })
            .catch(error => {
                console.error('Erro:', error);
                this.mostrarErro('Erro ao deletar estabelecimento');
            });
        }
    }

    mostrarErro(mensagem) {
        const container = document.getElementById('estabelecimentos-container');
        container.innerHTML = `<div class="alert alert-danger">${mensagem}</div>`;
    }
}

let gerenciadorEstab;

document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('estabelecimentos-container')) {
        gerenciadorEstab = new GerenciadorEstabelecimentos();
    }
});
