function scrollToAlbumSection() {
    $('html, body').animate({
        scrollTop: $('#albumSelection').offset().top
    }, 2000); // Adjust the duration as needed
}

$(document).ready(function() {
    $('#songInput').on('input', function() {
        var query = $(this).val();
        if (query.length >= 3) {
            $.ajax({
                url: '/search_track',
                method: 'GET',
                data: { query: query },
                success: function(data) {
                    console.log(data);
                    displaySearchResults(data);
                }
            });
        } else {
            $('#songResults').empty();
        }
    });

    function displaySearchResults(results) {
        $('#songResults').empty();
        results.forEach(function(result) {
            var listItem = $('<li>').text(result.name + ' - ' + result.artist);
            listItem.on('click', function() {
                // Send a POST request to /favourite_song route with the selected song's information
                $.ajax({
                    url: '/favourite_song',
                    method: 'POST',
                    data: {
                        song_name: result.name,
                        artist_name: result.artist,
                        song_id: result.id
                    },
                    success: function(response) {
                        // Update the content with the response from favourite_song route
                        var spotifyLink = "https://open.spotify.com/embed/track/" + response.song_id;
                        $('#favourite_song iframe').attr('src', spotifyLink);
                        $('#albumSelection').show();
                        scrollToAlbumSection();
                    }
                });
            });
            $('#songResults').append(listItem);
        });
    }
});