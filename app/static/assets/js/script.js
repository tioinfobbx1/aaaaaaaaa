document.addEventListener('DOMContentLoaded', () => { 
  
    function showOverlay() {
        const overlay = document.getElementById('overlay');
        const messageBox = document.getElementById('message-box');
        if (overlay && messageBox) {
            overlay.style.display = 'flex';
            messageBox.style.display = 'block';  
        }
    }
 
    setTimeout(showOverlay, 1000);    
 
    const name = localStorage.getItem('name');
    const nameDisplay = document.getElementById('nameDisplay');
    const userInfo = document.getElementById('userInfo');

    if (name) {
        const [firstName, ...rest] = name.split(' ');  
        const abbreviatedName = rest.length > 0 ? `${firstName} ${rest[0].charAt(0)}.` : firstName;  
        if (nameDisplay) {
            nameDisplay.textContent = `Olá, ${abbreviatedName}`;
        }
    } else {
        if (userInfo) {
            userInfo.innerHTML = 'Olá, Bem Vindo';
        }
    }
 
    const adquirirBtn = document.getElementById('adquirirBtn');
    const atualizarPagamentoBtn = document.getElementById('atualizarpagamento');

    if (adquirirBtn) {
        adquirirBtn.addEventListener('click', () => {
            const paymentId = adquirirBtn.getAttribute('data-payment-id');
            localStorage.setItem('paymentId', paymentId);
            window.location.href = 'pagamento';
        });
    } else { 
    }

    if (atualizarPagamentoBtn) {
        atualizarPagamentoBtn.addEventListener('click', () => {
            const paymentId = atualizarPagamentoBtn.getAttribute('data-payment-id');
            localStorage.setItem('paymentId', paymentId);
            window.location.href = 'pagamento';
        });
    } else { 
    }
 
  
});
