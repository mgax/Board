$(function() {

module("Note model");

test("Load note", function() {
    var fixture = '{properties: {a: "b"}, children: []}';
    stop();
    load_fixture(fixture, try_catch(function() {
        load_and_check_note('/root', {a: 'b'}, start); }));
});

test("Load sub note", function() {
    var fixture = '{properties: {}, children:[' +
            '{properties: {"-name-": "a"}, children: [' +
                '{properties: {"-name-": "c"}, children: []}' +
            ']}, ' +
            '{properties: {"-name-": "b"}, children: []}' +
        ']}';
    stop();
    load_fixture(fixture, try_catch(function() {
        var queue = [];
        queue.push(function(callback) {
            load_and_check_note('/root/a', {"-name-": "a"}, callback); });
        queue.push(function(callback) {
            load_and_check_note('/root/b', {"-name-": "b"}, callback); });
        queue.push(function(callback) {
            load_and_check_note('/root/a/c', {"-name-": "c"}, callback); });
        testQueue(queue, start);
    }));
});

function load_and_check_note(url, properties, callback) {
    board.load_note_at_url(url, try_catch(function(evt) {
        assertTrue(evt.success, "Note load event success");
        assertSame(evt.note.properties, properties);
        callback();
    }));
}

});
