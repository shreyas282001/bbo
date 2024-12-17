// static/scripts.js
function updateStatus(id, status) {
    $.ajax({
        url: '/update_status',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ id: id, status: status }),
        success: function (response) {
            if (response.success) {
                alert('Status updated successfully!');
            }
        }
    });
}
