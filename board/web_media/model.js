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
        evt = {success: true, note: new Note(url, data.properties)};
        callback(evt);
    }
}

function Note(url, properties) {
    this.url = url;
    this.properties = properties;
}

Note.prototype.pGet = function(key) {
    return this.properties[key];
}

Note.prototype.pGetAll = function() {
    output = {};
    for(name in this.properties)
        output[name] = this.properties[name];
    return output;
}

Note.prototype.pSet = function(key, value, callback) {
    var props_data = {}; props_data[key] = value;
    $.ajax({
        url: this.url,
        type: 'POST',
        data: {'action': 'set_props', 'data': $.toJSON(props_data)},
        success: function() {
            callback({success: true});
        },
        error: function() {
            callback({success: false});
        }
    });
}

})();
