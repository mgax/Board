var board = {}; // the Board API entry point

(function() {

board.load_note_at_url = function(url, callback) {
    $.ajax({
        url: url,
        type: 'GET',
        dataType: 'json',
        success: ajax_result,
        error: function(evt) {
            callback({success: false});
        }
    });

    function ajax_result(data) {
        evt = {success: true, note: data}
        callback(evt);
    }
}

})();
