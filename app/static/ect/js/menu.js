const desktop = window.matchMedia('(min-width: 1024px)').matches;
const hambuguer = document.querySelector('#menu .hamburger');
const ctnM = document.querySelector('#menu > .menu');
const menuUsuario = document.querySelector('#menu a.nome');
const ddUsu = document.querySelector('#menu > .dd');
const menuUsuarioMob = document.querySelector('#menu > .menu section a.nome-usuario-logado');
const ddUsuMob = document.querySelector('#menu .menu div.dd-mobile');
let pilha = [];

const enterClick = el => {
    el.addEventListener('keydown', ev => {
        if (ev.key == 'Enter') {
            ev.preventDefault();
            el.dispatchEvent(new Event('click'));
        }
    });
};

function abreMenu () {
    hambuguer.classList.add('aberto');
    ctnM.classList.remove('oculto');
    document.body.classList.add('menu-aberto');
    addHash();
    conf.aberto = true;
    saveConf();
}

function fechaMenu () {
    hambuguer.classList.remove('aberto');
    ctnM.classList.add('oculto');
    document.body.classList.remove('menu-aberto');
    const abertos = ctnM.querySelectorAll('.aberto');
    for (let a of abertos) {
        a.classList.remove('aberto');
    }
    pilha = [];
    removeHash();
    conf.aberto = false;
    conf.abertos = [];
    saveConf();
}

function abreSubmenu (ev, anchor) {
    let a;
    if (ev) {
        a = ev.currentTarget;
    } else {
        a = anchor;
    }
    if (a.classList.contains('nome-usuario-logado')) return;
    let sub = a.nextSibling.nextSibling;
    if (sub.tagName != 'DIV') return;
    sub.classList.add('aberto');
    pilha.push(sub.querySelector('.voltar'));
    sub.querySelectorAll(':scope > a').forEach(a => a.tabIndex = 1);
    setTimeout(() => {
        sub.querySelector('.voltar').focus();
    }, 0);
    if (ev) {
        addHash();
        conf.abertos.push([...a.parentNode.childNodes].indexOf(a));
        saveConf();
    }
    ctnM.scrollTop = 0;
}

function fechaSubmenu (ev) {
    let a;
    if (ev) {
        a = ev.currentTarget;
    } else {
        a = pilha.pop();
    }
    let sub = a.parentNode;
    sub.classList.remove('aberto');
    sub.querySelectorAll('a').forEach(a => a.tabIndex = -1);
    if (ev) {
        subHash();
    }
    conf.abertos.pop();
    saveConf();
}

function getHash () {
    const pars = new URLSearchParams(location.hash.substr(1));
    return pars.get('menu');
}

function removeHash () {
    if (desktop) return;
    if (location.hash) {
        const pars = new URLSearchParams(location.hash.substr(1));
        if (pars.has('menu')) {
            const newPars = new URLSearchParams();
            for (let [k, v] of pars.entries()) {
                if (k == 'menu') continue;
                newPars.set(k, v);
            }
            history.pushState(null, null, '#' + newPars.toString());
        }
    }
}

function addHash () {
    if (desktop) return;
    const pars = new URLSearchParams(location.hash.substr(1));
    let nivel = 1;
    if (!pars.has('menu')) {
        pars.set('menu', nivel.toString());
    } else {
        const nivel = parseInt(pars.get('menu')) + 1;
        pars.set('menu', nivel.toString());
    }
    history.pushState(nivel.toString(), null, '#' + pars.toString());
}

function subHash () {
    if (desktop) return;
    const pars = new URLSearchParams(location.hash.substr(1));
    if (!pars.has('menu')) return;
    history.back();
}

function abreFechMenUsu (ev) {
    ev.stopPropagation();
    if (menuUsuario.classList.contains('aberto')) {
        menuUsuario.classList.remove('aberto');
        ddUsu.classList.remove('aberto');
    } else {
        menuUsuario.classList.add('aberto');
        ddUsu.classList.add('aberto');
    }
}

function abreFechMenUsuMob (ev) {
    ev.stopPropagation();
    if (menuUsuarioMob.classList.contains('aberto')) {
        menuUsuarioMob.classList.remove('aberto');
        ddUsuMob.classList.remove('aberto');
    } else {
        menuUsuarioMob.classList.add('aberto');
        ddUsuMob.classList.add('aberto');
    }
}

let conf = {
    aberto: false,
    abertos: [],
};

function readConf () {
    const cnf = localStorage.getItem('menu');
    if (!cnf) return;
    conf = JSON.parse(cnf);
}

function saveConf () {
    localStorage.setItem('menu', JSON.stringify(conf));
}

function ini () {
    if (!ctnM) return;
    readConf();

    if (hambuguer) {
        hambuguer.addEventListener('click', ev => {
            const ham = ev.currentTarget;
            if (ham.classList.contains('aberto')) {
                fechaMenu();
            } else {
                abreMenu();
            }
        });
    }
    ctnM.classList.add('oculto');
    setInterval(() => {
        const altura = window.innerHeight - hambuguer.getBoundingClientRect().bottom;
        ctnM.style.height = (altura - 9) + 'px';
    }, 500);
    document.body.addEventListener('click', () => {
        if (!desktop) {
            fechaMenu();
        }
    });
    hambuguer.addEventListener('click', ev => ev.stopPropagation());
    ctnM.addEventListener('click', ev => ev.stopPropagation());
    const subs = ctnM.querySelectorAll('div');
    for (let s of subs) {
        if (s.classList.contains('dd-mobile')) {
            continue;
        }
        let voltar = document.createElement('a');
        voltar.textContent = 'Voltar';
        voltar.className = 'voltar';
        s.insertAdjacentElement('afterbegin', voltar);
    }
    ctnM.querySelectorAll('a').forEach(a => {
        a.tabIndex = 1;
    });
    ctnM.querySelectorAll(':scope > div a').forEach(a => {
        a.tabIndex = -1;
    });
    const abriveis = ctnM.querySelectorAll('a:not([href])');
    for (let a of abriveis) {
        if (a.classList.contains('voltar')) {
            a.addEventListener('click', fechaSubmenu);
        } else {
            a.addEventListener('click', abreSubmenu);
        }
        enterClick(a);
    }

    window.addEventListener('popstate', ev => {
        if (desktop) return;
        const nivel = parseInt(getHash());
        const n = pilha.length;
        if (n == nivel) {
            fechaSubmenu();
        } else {
            fechaMenu();
        }
    });

    removeHash();

    if (desktop && conf.aberto) abreMenu();
    try {
        let sub = ctnM;
        for (let i = 0; i < conf.abertos.length; i++) {
            let a = sub.childNodes[conf.abertos[i]];
            abreSubmenu(null, a);
            if (!desktop) {
                addHash();
            }
            sub = a.nextSibling.nextSibling;
        }
    } catch (e) {
        conf.abertos = [];
        saveConf();
    }
    enterClick(hambuguer);
    if (menuUsuario) {
        menuUsuario.addEventListener('click', abreFechMenUsu);
        menuUsuarioMob.addEventListener('click', abreFechMenUsuMob);
        ddUsu.addEventListener('click', ev => ev.stopPropagation());
        ddUsuMob.addEventListener('click', ev => ev.stopPropagation());
        document.body.addEventListener('click', () => {
            menuUsuario.classList.remove('aberto');
            menuUsuarioMob.classList.remove('aberto');
            ddUsu.classList.remove('aberto');
            ddUsuMob.classList.remove('aberto');
        });
        enterClick(menuUsuario);
    }
}

try {
    ini();
} catch (e) {
    console.log("Erro ao tentar construir o menu");
    console.log(e)
}