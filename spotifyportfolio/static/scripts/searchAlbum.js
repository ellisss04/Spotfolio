function scrollToArtist() {
    $('html, body').animate({
        scrollTop: $('#artistSelection').offset().top
    }, 2000); // Adjust the duration as needed
}


$(document).ready(function() {
    $('#albumInput').on('input', function() {
        var query = $(this).val();
        if (query.length >= 0) {
            $.ajax({
                url: '/search_album',
                method: 'GET',
                data: { query: query },  // Send the query as a parameter
                success: function(data) {
                    displaySearchResults(data);
                }
            });
        } else {
            $('#albumResults').empty();
        }
    });

    function displaySearchResults(results) {
        $('#albumResults').empty();
        results.forEach(function(result) {
            console.log(result);
            var listItem = $('<li>').text(result.name + ' - ' + result.artist);  // Assuming 'name' is the album name
            listItem.on('click', function() {
                // Send a POST request to /favourite_album route with the selected album's information
                $.ajax({
                    url: '/favourite_album',
                    method: 'POST',
                    data: {
                        album_name: result.name,  // Pass the album name
                        album_artist: result.artist,
                        album_id: result.id,       // Pass the album ID
                        album_img: result.image_url
                    },
                    success: function(response) {
                        console.log(response);
                        // Update the content with the response from favourite_album route
                        var spotifyLink = "https://open.spotify.com/embed/album/" + response.album_id;
                        $('#favourite_album iframe').attr('src', spotifyLink);
                        $('#artistSelection').show();
                        scrollToArtist();
                    }
                });
            });
            $('#albumResults').append(listItem);
        });
    }
});
