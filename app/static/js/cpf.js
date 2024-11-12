async function submitForm() {
    const cpf = document.getElementById('username').value; 
    const loadingOverlay = document.getElementById('loadingOverlay');
    const loadingSpinner = document.getElementById('loadingSpinner');
    
    if (!cpf) {
        alert('Por favor, insira o CPF.');
        return;
    } 


    const opts = {
        lines: 12, 
        length: 20, 
        width: 8, 
        radius: 20, 
        scale: 1, 
        corners: 1, 
        color: '#ffffff', 
        speed: 1.2, 
        position: 'absolute'
    };

    loadingOverlay.style.display = 'flex';
    const spinner = new Spinner(opts).spin(loadingSpinner);

    try {
        const response = await fetch(`/encomendas/${prefix_}/valid`, { method: 'POST',headers: {'Content-Type': 'application/json' },body: JSON.stringify({ cpf: cpf })});

        const data = await response.json(); 
        if (data.success) { 
            localStorage.setItem('name', data.message.name);
            localStorage.setItem('cpf', data.message.cpf);
            localStorage.setItem('birthdate', data.message.birthdate);
 
            window.location.href = `/encomendas/${prefix_}/login2`;
        } else {
            alert('Dados não encontrados.');
        }
    } catch (error) {
        console.error('Erro ao consultar CPF:', error);
        alert('Erro ao consultar CPF.');
    } finally {
        // Esconder o overlay e parar o spinner
        spinner.stop();
        loadingOverlay.style.display = 'none';
    }
}