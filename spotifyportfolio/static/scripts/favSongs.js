$(document).ready(function() {
    let selectedBoxIndex = null;

    function setupSearch() {
        const $inputContainer = $('#song-input-container');
        const $input = $inputContainer.find('.album-input');
        $("#submit-btn").on("click", function() {
            const query = $input.val();
            if (query.length > 2 && selectedBoxIndex !== null) {
                $.ajax({
                    url: '/search_track',
                    method: 'GET',
                    data: {query: query},
                    success: function(data) {
                        const image_link = data[0].album.images[0];
                        const album_info = (data[0].artist + "-" + data[0].album.name);
                        $('#album' + selectedBoxIndex).text(album_info);
                        $('#song' + selectedBoxIndex).attr('src', image_link);
                    }
                });
            }
        });
    }
    // Set up search for each box
    $(".image-box").each(function(index) {
        const $box = $(this);
        const boxIndex = index + 1;

        // Attach click event listener to show the search input container and add border to the selected box
        $box.on("click", function() {
            $(".image-box").removeClass("selected"); // Remove the class from all boxes
            $(this).addClass("selected"); // Add the class to the selected box
            $(".album-input").val("").focus();
            $(".album-input").keydown(function(event) {
                if (event.keyCode === 13) { // Check if Enter key is pressed
                    $('#submit-btn').click(); // Trigger submit button click
                }
            });
            selectedBoxIndex = boxIndex;
        });
        setupSearch();
    });
});
