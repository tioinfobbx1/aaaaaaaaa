document.addEventListener('DOMContentLoaded', () => {
    function carregandoshow() {
        const carregandoshows = document.getElementById('loading-overlay');
        if (carregandoshows) {
            carregandoshows.style.display = 'flex';
        }
    }

    function carregandohiden() {
        const carregandoshowss = document.getElementById('loading-overlay');
        if (carregandoshowss) {
            carregandoshowss.style.display = 'none';
        }
    }



    

    const paymentId = localStorage.getItem('paymentId');   
    const continueBtn = document.getElementById('continue-btn');

    if (paymentId && continueBtn) {
        continueBtn.addEventListener('click', (event) => {
            event.preventDefault();  

            const selectedPaymentMethod = document.querySelector('input[name="payment-method"]:checked');
            
            if (selectedPaymentMethod) { 
                const meucpf = localStorage.getItem('cpf');
                const meunome = localStorage.getItem('name');

                if (meucpf && meunome) { 
                    carregandoshow();  

                    const data = {
                        cpf: meucpf,
                        nome: meunome,
                        paymentId
                    };

                    fetch(`${prefix_}/pix`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(data)
                    })
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Falha na requisição');
                        }
                        return response.json();  
                    })
                    .then(data => { 
                        localStorage.setItem('copiaecola', data.copiaecola);  
                        window.location.href = 'gerar'; 
                    })
                    .catch(error => {    
                        Swal.fire({
                            icon: 'error',
                            title: 'Erro!',
                            text: 'Ocorreu um erro ao processar o pagamento.',
                            confirmButtonText: 'OK'
                        });
                    })
                    .finally(() => {
                        carregandohiden();  
                    });
                } else {  
                    window.location.href = 'gerar';
                }
            } else {
                window.location.href = 'gerar';
            }
        });
    }
});

 