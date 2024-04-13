$(document).ready(function() {
    let selectedBoxIndex = null;

    function setupSearch() {
        const $inputContainer = $('#album-input-container');
        const $input = $inputContainer.find('.album-input');
        $("#submit-btn").on("click", function() {
            const query = $input.val();
            if (query.length > 2 && selectedBoxIndex !== null) {
                $.ajax({
                    url: '/search_album',
                    method: 'GET',
                    data: {query: query, limit: 1},
                    success: function(data) {
                        // delete album based on the album name in the text
                        deleteAlbum();
                        saveAlbum(data);
                        const image_link = data[0].image_url;
                        const album_info = (data[0].artist + "-" + data[0].name);
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
    });
    function saveAlbum(result) {
        $.ajax({
            url: '/save_album',
            method: 'POST',
            data: {
                album_name: result[0].name,  // Pass the album name
                album_artist: result[0].artist,
                album_id: result[0].id,       // Pass the album ID
                album_img: result[0].image_url
            },
            success: function(response) {
                console.log(response.message);
            },
            error: function(xhr, status, error) {
                console.error(xhr.responseText);
            }
        });
    }

    function deleteAlbum() {
        const image_url = document.getElementById(('song' + selectedBoxIndex)).getAttribute('src');
        if (image_url !== ""){
            $.ajax({
            url: '/delete_album',
            method: 'POST',
            data: {image_url: image_url},
            success: function(response) {
                console.log(response.message);
            },
            error: function(xhr, status, error) {
                console.error(xhr.responseText);
            }

        });
        }
        else{
            return 0
        }

    }
    setupSearch();
});


