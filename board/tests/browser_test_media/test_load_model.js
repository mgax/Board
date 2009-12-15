$(function() {

module("Note model");

test("Load note", function() {
    var fixture = '{properties: {a: "b"}, children: []}';
    stop();
    load_fixture(fixture, try_catch(function() {
        load_and_check_note('/root', {a: 'b'}, start); }));
});

test("Load note with multiple properties", function() {
    var fixture = '{properties: {}, children: [' +
        '{properties: {a: "b", "-name-": "yarr", x: "Y"}, ' +
        'children: []}]}';
    expect_properties = {'a': 'b', '-name-': 'yarr', 'x': 'Y'};
    stop();
    load_fixture(fixture, try_catch(function() {
        board.load_note_at_url('/root/yarr', try_catch(function(evt) {
            assertTrue(evt.success, "Note load event success");
            var note = evt.note;
            for(key in expect_properties)
                assertEqual(note.pGet(key), expect_properties[key]);
            assertSame(note.pAll(), expect_properties);
            start();
        }));
    }));
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

test("Change note", function() {
    var fixture = '{properties: {}, children:[' +
            '{properties: {"-name-": "a"}, children: [' +
                '{properties: {"-name-": "c"}, children: []}' +
            ']}, ' +
            '{properties: {"-name-": "b"}, children: []}' +
        ']}';
    stop();
    load_fixture(fixture, try_catch(function() {
        board.load_note_at_url('/root/a', try_catch(function(evt) {
            assertTrue(evt.success, "Note load event success");
            var note = evt.note;
            note.pSet('x', 'y', try_catch(function(evt) {
                assertTrue(evt.success, "Note pSet event success");
                $.getJSON('/root/a', function(data) {
                    assertEqual(data.properties['x'], 'y');
                    start();
                });
            }));
        }));
    }));
});

function load_and_check_note(url, properties, callback) {
    board.load_note_at_url(url, try_catch(function(evt) {
        assertTrue(evt.success, "Note load event success");
        var note = evt.note;
        for(key in properties)
            assertEqual(note.pGet(key), properties[key]);
        callback();
    }));
}

});
