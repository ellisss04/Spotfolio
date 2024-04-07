function scrollToSubmit() {
    $('html, body').animate({
        scrollTop: $('#Submit-hidden').offset().top
    }, 2000); // Adjust the duration as needed
}

$(document).ready(function() {
    $('#artistInput').on('input', function() {
        var query = $(this).val();
        if (query.length >= 0) {
            $.ajax({
                url: '/search_artist',
                method: 'GET',
                data: { query: query },
                success: function(data) {
                    displaySearchResults(data);
                }
            });
        } else {
            $('#artistResults').empty();
        }
    });

    function displaySearchResults(results) {
        $('#artistResults').empty();
        results.forEach(function(result) {
            var listItem = $('<li>').text(result.artist);
            listItem.on('click', function() {
                // Send a POST request to /favourite_artist route with the selected artists's information
                $.ajax({
                    url: '/favourite_artist',
                    method: 'POST',
                    data: {
                        artist_name: result.artist,
                        artist_id: result.id,

                    },
                    success: function(response) {
                        console.log(response)
                        // Update the content with the response from favourite_artist route#
                        var spotifyLink = "https://open.spotify.com/embed/artist/" + response.artist_id;
                        $('#favourite_artist iframe').attr('src', spotifyLink);
                        $('#Submit-hidden').show();
                        scrollToSubmit();
                    }
                });
            });
            $('#artistResults').append(listItem);
        });
    }
});