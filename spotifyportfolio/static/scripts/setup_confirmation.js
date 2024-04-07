    $(document).ready(function() {
        // Ajax request to check if setup confirmation is required
        $.get('/setup', function(response) {
            if (response.setup_confirmation) {
                // If setup confirmation is required, show the modal
                $('#setupConfirmationModal').modal('show');
            }
        });
    });