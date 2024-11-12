 
document.addEventListener('DOMContentLoaded', () => {
function formatCPF(cpf) {
    if (!cpf || cpf.length !== 11) return cpf;
    return cpf.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
}

const pixCodeInput = document.getElementById('pix-code');
const qrcodeContainer = document.getElementById('qrcode');
const nomeDoc = document.getElementById('nomeDoc2');
const numeroDoc = document.getElementById('numeroDoc2'); 
const nome = localStorage.getItem('name');
const cpf = localStorage.getItem('cpf');
const copiaecola = localStorage.getItem('copiaecola');

if (nomeDoc && nome) {
    nomeDoc.textContent = nome;
}

if (numeroDoc && cpf) {
    numeroDoc.textContent = formatCPF(cpf);
}

if (copiaecola) { 
    pixCodeInput.value = copiaecola; 
    new QRCode(qrcodeContainer, {
        text: copiaecola,
        width: 256,
        height: 256
    });
} else { 
}

document.getElementById('copy-code-btn').addEventListener('click', () => {
    pixCodeInput.select();
    document.execCommand('copy');
    Swal.fire({
        icon: 'success',
        title: 'Código PIX Copiado!',
        text: 'O código PIX foi copiado para a área de transferência.',
        confirmButtonText: 'OK'
    });
});

document.getElementById('continue-btn').addEventListener('click', () => {
    window.location.href = 'login';  
});});