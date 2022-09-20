function modalConfirmRemoveHouse(id) {
    let modal = document.getElementById("modal-confirm-remove-house");
    modal.style.display = "block";

    let btnConfirmationRemoveHouse = document.getElementById("btn-confirmation-remove-house");
    btnConfirmationRemoveHouse.innerHTML = `
        <input type="hidden" name="id_of_house_to_remove" value="${id}" />
        <input type="submit" class="btn btn-danger" value="Supprimer" />
    `;
}


function closeModalConfirmRemoveHouse() {
    let modal = document.getElementById("modal-confirm-remove-house");
    modal.style.display = "none";
}

function removeHouse(url) {
    window.location.href = url;
}