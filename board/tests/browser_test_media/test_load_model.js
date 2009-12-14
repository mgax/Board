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

});
