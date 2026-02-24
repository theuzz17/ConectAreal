const formularioLogin = document.getElementById('formularioLogin');
const mensagemErro = document.getElementById('mensagemErro');

formularioLogin.addEventListener('submit', async (evento) => {
    evento.preventDefault();

    const usuario = document.getElementById('usuario').value;
    const senha = document.getElementById('senha').value;

    try {
        const resposta = await fetch('/api/admin/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                usuario: usuario,
                senha: senha
            })
        });

        const dados = await resposta.json();

        if (dados.sucesso) {
            window.location.href = '/admin';
        } else {
            mensagemErro.textContent = dados.erro;
            mensagemErro.style.display = 'block';
        }
    } catch (erro) {
        mensagemErro.textContent = 'Erro ao conectar com o servidor';
        mensagemErro.style.display = 'block';
        console.error('Erro:', erro);
    }
});
