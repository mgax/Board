$(function() {

module("Note model");

test("Load model", function() {
    var fixture = '{properties: {a: "b"}, children: []}';
    stop();
    load_fixture(fixture, try_catch(function() {
        board.load_note_at_url('/root', try_catch(function(evt) {
            assertTrue(evt.success, "Note load event success");
            assertSame(evt.note.properties, {a: 'b'});
            start();
        }));
    }));
});

function try_catch(callback) {
    return function() {
        try {
            callback.apply(this, arguments);
        }
        catch(e) {
            console.error(e);
            assertTrue(false, "Exception caught:" + e);
            start();
        }
    }
}

function load_fixture(data, callback) {
    $.ajax({
        url: '/load_fixture',
        type: 'POST',
        data: {'fixture': data},
        success: callback,
        error: function(evt) {
            assertTrue(false, "AJAX call failed");
            start();
        }
    });
}

});
