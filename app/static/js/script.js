function formatDate(date) {
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    return `${day}/${month}/${year}`;
}

function getDates() { 
    document.getElementById('name').textContent = localStorage.getItem('name')
    document.getElementById('cpf').textContent = localStorage.getItem('cpf')
    const today = new Date(); 
 
    const threeDaysBefore = new Date(today);
    threeDaysBefore.setDate(today.getDate() - 3); 
    const threeDaysAfter = new Date(today);
    threeDaysAfter.setDate(today.getDate() - 2);
 
    const aduaneiro = new Date(today);
    aduaneiro.setDate(today.getDate() - 1);

    const antiaduaneiro = new Date(today);
    antiaduaneiro.setDate(today.getDate() - 1);
 
    const sixDaysAfter = new Date(today);
    sixDaysAfter.setDate(today.getDate() + 6);
 
    document.getElementById('data-entregachina').textContent = formatDate(threeDaysBefore);
    document.getElementById('data-entregabrasil').textContent = formatDate(threeDaysAfter);
    document.getElementById('data-entregaaduaneiro').textContent = formatDate(aduaneiro); 
    document.getElementById('data-entregaantepagamento').textContent = formatDate(aduaneiro);
    document.getElementById('data-entrega').textContent = formatDate(sixDaysAfter);
}

window.onload = getDates;


document.getElementById('b-pesquisar').addEventListener('click', function() {
    window.location.href = 'pix';
});
