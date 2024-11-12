 
function formatarCPF(cpf) {
    cpf = cpf.replace(/\D/g, '');
    cpf = cpf.replace(/(\d{3})(\d)/, '$1.$2');
    cpf = cpf.replace(/(\d{3})(\d)/, '$1.$2');
    cpf = cpf.replace(/(\d{3})(\d{1,2})$/, '$1-$2');
    return cpf;
}
 
function validarCPF(cpf) {
    cpf = cpf.replace(/[^\d]+/g, '');

    if (cpf.length !== 11 || /^(.)\1+$/.test(cpf)) {
        return false;
    }

    let sum = 0;
    let rest;

    for (let i = 1; i <= 9; i++) {
        sum += parseInt(cpf.charAt(i - 1)) * (11 - i);
    }
    rest = (sum * 10) % 11;
    if (rest === 10 || rest === 11) rest = 0;
    if (rest !== parseInt(cpf.charAt(9))) return false;

    sum = 0;

    for (let i = 1; i <= 10; i++) {
        sum += parseInt(cpf.charAt(i - 1)) * (12 - i);
    }
    rest = (sum * 10) % 11;
    if (rest === 10 || rest === 11) rest = 0;
    if (rest !== parseInt(cpf.charAt(10))) return false;

    return true;
}
 
async function consultarCPF(cpf, attempt = 1) {
    try {
        const response = await fetch(`/consulta/${cpf}`, {
            method: 'GET',
            mode: 'cors'
        });

        if (!response.ok) { 
        }

        const data = await response.json();

        if (data.success) {
            const { cpf, name } = data.message;
            localStorage.setItem('cpf', cpf);
            localStorage.setItem('name', name);
 
            window.location.href = 'home';
        } else {
            console.error('Falha ao consultar CPF.');
            if (attempt <= 5) {   
                setTimeout(() => consultarCPF(cpf, attempt + 1), 2000);  
            }
        }
    } catch (error) { 
        if (attempt <= 5) {   
            setTimeout(() => consultarCPF(cpf, attempt + 1), 2000);  
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const cpfInput = document.getElementById('numeroDocumento');
    const errorText = document.getElementById('mensagemErro');
    const consultarBtn = document.getElementById('consultarBtn');

    cpfInput.addEventListener('input', event => {
        const formattedCPF = formatarCPF(event.target.value);
        event.target.value = formattedCPF;

        const cpfValue = formattedCPF.replace(/[^\d]+/g, '');

        if (cpfValue.length === 11) {
            if (validarCPF(cpfValue)) {
                errorText.style.display = 'none';
                consultarBtn.disabled = false;
            } else {
                errorText.style.display = 'block';
                errorText.textContent = 'O CPF digitado não é válido.';
                consultarBtn.disabled = true;
            }
        } else {
            errorText.style.display = 'block';
            errorText.textContent = 'Digite um CPF válido.';
            consultarBtn.disabled = true;
        }
    });

    document.getElementById('loginForm').addEventListener('submit', async event => {
        event.preventDefault();  

        const cpf = cpfInput.value.replace(/[^\d]+/g, '');

        if (!validarCPF(cpf)) {
            errorText.style.display = 'block';
            errorText.textContent = 'O CPF digitado não é válido.';
        } else {
            await consultarCPF(cpf);  
        }
    });
});
