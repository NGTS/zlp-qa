$(function() {
    $('button.button-showhide').each(function(index, button) {
        var item_id = button.id;
        var item_name = item_id.substring(item_id.indexOf('-') + 1, item_id.length);
        var image_id = 'img-' + item_name;
        $(button).click(function(event) {
            var elem = $('img#' + image_id);
            elem.toggle({
                duration: 0,
                complete: function() {
                    if (elem.is(":visible")) {
                        $(button).html('hide');
                    } else {
                        $(button).html('show');
                    }
                }
            });
        });
    });
});
