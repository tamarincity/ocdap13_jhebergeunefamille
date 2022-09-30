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

function showMessageField(suffix) {
    let button = document.getElementById(`toggle-button_${suffix}`);
    button.style.display = "none"

    let form = document.getElementById(`send-message-to-host_${suffix}`)
    form.style.display = "block"

    let btnCancel = document.getElementById(`btn-cancel_${suffix}`)
    btnCancel.classList = "btn btn-danger"
    btnCancel.style.display = "block"
}

function cancelMessage(suffix) {
    let button = document.getElementById(`toggle-button_${suffix}`);
    button.style.display = "block"

    let form = document.getElementById(`send-message-to-host_${suffix}`)
    form.style.display = "none"

    let btnCancel = document.getElementById(`btn-cancel_${suffix}`)
    btnCancel.style.display = "none"
}
