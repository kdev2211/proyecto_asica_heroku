   // CUSTOM JAVASCRIPT PARA EL HTML QUE CONTROLA EL HTML: ticket_formulario
   
   // CARGA LAS OPCIONES DE EL SELECT DE USUARIOS BASADO EN LA OPCION ESCOGIDA EN EL SELECT DE DEPARTAMENTOS
   document.addEventListener('DOMContentLoaded', function() {
      var departamentoSelect = document.getElementById('select_departamento');
      var usuarioAsignadoSelect = document.getElementById('select_usuario');
  
      // Inicialmente, deshabilitar el select de usuario si el valor de departamento es vacío
      usuarioAsignadoSelect.disabled = departamentoSelect.value === "";
  
      departamentoSelect.addEventListener('change', function() {
          var departamentoId = departamentoSelect.value;
  
          if (departamentoId !== "") {
              usuarioAsignadoSelect.disabled = false;
  
              fetch(`/helpdesk/view_cargar_usuarios_ajax/${departamentoId}/`)
                  .then(response => response.json())
                  .then(data => {
                      usuarioAsignadoSelect.innerHTML = '<option value="" selected>Seleccione un usuario</option>';
  
                      data.usuarios.forEach(function(usuario) {
                          var option = document.createElement('option');
                          option.value = usuario.id;
                          option.text = `${usuario.first_name} ${usuario.last_name} (Usuario: ${usuario.username} | ${usuario.nombre_puesto})`;

                         

                          usuarioAsignadoSelect.appendChild(option);
                      });
                  })
                  .catch(error => {
                      console.error('Error al cargar usuarios:', error);
                      usuarioAsignadoSelect.innerHTML = '<option value="">Error al cargar usuarios</option>';
                  });
          } else {
              usuarioAsignadoSelect.disabled = true;
              usuarioAsignadoSelect.innerHTML = '<option value="" selected>Seleccione un usuario</option>';
          }
      });
  
      // Función para manejar el envío del formulario mediante AJAX
      function enviarFormulario() {
          document.getElementById('spinner-div').style.display = 'flex';
          var form = document.getElementById('formulario_nota');
          var formData = new FormData(form);
          document.getElementById('descripcion_notas').classList.remove('is-invalid');

          
          

          fetch(form.action, {
              method: 'POST',
              headers: {
                  'X-CSRFToken': form.querySelector('[name=csrfmiddlewaretoken]').value
              },
              body: formData
          })
          .then(response => response.json())
          .then(data => {
              if (data && data.descripcion_notas) {
                  var nuevaNota = document.createElement('div');
                  nuevaNota.classList.add('card');
                  nuevaNota.style.boxShadow = 'none';
                  nuevaNota.style.marginLeft = '10px';
                  nuevaNota.style.marginRight = '10px';
                  nuevaNota.innerHTML = `
                      <div class="card-header">${data.fecha_nota}</div>
                      <div class="card-body">
                          <h5 class="card-title">${data.autor}</h5>
                          <div>${data.descripcion_notas}</div>
                      </div>
                  `;
                  document.querySelector('.card_custom').prepend(nuevaNota);
                  document.getElementById('descripcion_notas').value = '';  // Limpiar el textarea
              } else {
                  console.log('La información fue almacenada correctamente, pero no se recibió ninguna nueva nota.');
              }
          })
          .catch(error => console.log('Error:', error))
          .finally(() => {
      
          });
      
      
          setTimeout(function() {
              document.location.reload();
          }, 1000);
      }

  
      // VALIDACIÓN Y ENVÍO DEL FORMULARIO
      function validateAndSubmitForm(event) {
          event.preventDefault();
  
          var nombre = document.getElementById('nombre_contacto').value.trim();
          var apellido = document.getElementById('apellido_contacto').value.trim();
          var email = document.getElementById('email_contacto').value.trim();
          var telefono = document.getElementById('telefono_contacto').value.trim();
          var descripcion = document.getElementById('descripcion_notas').value.trim();
          var accion = document.getElementById('accion').value.trim();
          var modalMessage = document.getElementById('modalMessage');
  
          var emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.(com|edu|org|net|gov|mil|biz|info)$/;
  
          if (nombre === "" || apellido === "" || email === "" || telefono === "") {
              modalMessage.textContent = "Por favor, llene los espacios requeridos en el formulario.";
              new bootstrap.Modal(document.getElementById('modalValidacion')).show();
  
              document.getElementById('nombre_contacto').classList.toggle('is-invalid', nombre === "");
              document.getElementById('apellido_contacto').classList.toggle('is-invalid', apellido === "");
              document.getElementById('email_contacto').classList.toggle('is-invalid', email === "");
              document.getElementById('telefono_contacto').classList.toggle('is-invalid', telefono === "");
              
              return false;
          }
  
          if (!emailPattern.test(email)) {
              modalMessage.textContent = "Por favor, ingrese un email válido.";
              new bootstrap.Modal(document.getElementById('modalValidacion')).show();
              document.getElementById('email_contacto').classList.add('is-invalid');
              return false;
          } else {
              document.getElementById('email_contacto').classList.remove('is-invalid');
          }
  
          if (accion === "enviar" && descripcion === "") {
              modalMessage.textContent = "Por favor, ingrese su respuesta.";
              new bootstrap.Modal(document.getElementById('modalValidacion')).show();
              document.getElementById('descripcion_notas').classList.add('is-invalid');
              return false;
          }
  
          var confirmModal = new bootstrap.Modal(document.getElementById('modalConfirmacion'));
          confirmModal.show();
          
          document.getElementById('confirmarEnvio').addEventListener('click', function() {
              confirmModal.hide();
              enviarFormulario();
          }, { once: true }); // Asegúrate de que este evento solo se maneje una vez
  
          return false;
      }
  
      var guardarBtn = document.getElementById('guardar');
      var enviarBtn = document.getElementById('enviar');
  
      guardarBtn.addEventListener('click', function() {
          document.getElementById('accion').value = "guardar";
          validateAndSubmitForm(event);
      });
  
      enviarBtn.addEventListener('click', function() {
          document.getElementById('accion').value = "enviar";
          validateAndSubmitForm(event);
      });
  });

