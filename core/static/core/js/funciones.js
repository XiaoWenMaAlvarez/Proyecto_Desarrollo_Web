function eliminarPeriodista(id) {
  Swal.fire({
    title: "¿Desea eliminar al periodista?",
    text: "Esta acción no se puede revertir",
    icon: "error",
    showCancelButton: true,
    confirmButtonColor: "#01881c",
    cancelButtonColor: "#d33",
    confirmButtonText: "Si, eliminar periodista"
  }).then((result) => {
    if (result.isConfirmed) {
      Swal.fire({
        title: "Periodista eliminado",
        text: "Se ha eliminado la cuenta exitosamente",
        icon: "success"
      }).then(function() {
      window.location.href = "/eliminar_periodista/" + id + "/";
    });
    }
  });
  
}

function eliminarNoticia(id) {
  Swal.fire({
    title: "¿Desea eliminar la noticia?",
    text: "Esta acción no se puede revertir",
    icon: "error",
    showCancelButton: true,
    confirmButtonColor: "#01881c",
    cancelButtonColor: "#d33",
    confirmButtonText: "Si, eliminar noticia"
  }).then((result) => {
    if (result.isConfirmed) {
      Swal.fire({
        title: "Noticia eliminada",
        text: "Se ha eliminado la noticia exitosamente",
        icon: "success"
      }).then(function() {
      window.location.href = "/eliminar_noticia/" + id + "/";
    });
    }
  });
  
}

const primer_slide = document.querySelectorAll(".carousel-item:first-child")
const arreglo = [...primer_slide]

for(let i = 0; i < arreglo.length; i++) {
  arreglo[i].classList.add("active")
}

