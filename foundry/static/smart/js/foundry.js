$(document).ready(function(){

    if (typeof FastClick !== 'undefined') {
        // Let fastclick add a touchstart/end click event
        // for more responsive touch interaction on smart devices
        FastClick.attach(document.body);

        $("a").bind("touchstart", function(e){$(this).addClass("touch-active");});
        $("a").bind("touchend touchcancel", function(e){$(this).removeClass("touch-active");});
    }

    var last_activity_time = $.now();

    if ($.support.ajax)
    {

    // Update last activity time
    $(document).mousemove(function(event){
        last_activity_time = $.now();
    });

    // Ajaxify paging for (1) standalone listing (2) listing in a tile.
    $(document).on('click', 'div.foundry-listing div.pagination a', function(e){
        e.preventDefault();
        var url_provider = $(this).parents('div.foundry-page-tile:first');
        if (url_provider.length)
        {
            var url = url_provider.attr('original_url');
            var target = $('div.foundry-listing:first', url_provider);
        }
        else
        {
            target = $(this).parents('div.foundry-listing:first');
            url = $(location).attr('href');
        }
        var listing_dom_id = target.attr('id');
        if (listing_dom_id == "foundry-listing-")
            listing_dom_id = null;
        var target_items = $('div.items:last', target);
        var target_pagination = $('div.pagination', target);
        // Strip params. Already present in href.
        url = url.split('?')[0];
        url = url + $(this).attr('href');
        $.get(
            url,
            {},
            function(data){
                // Markup that contains fluff. We want only the content.
                var el = $('<div>' + data + '</div>');

                // If the listing can be identified then use that, else use
                // first available one.
                if (listing_dom_id)
                {
                    var content = $('#' + listing_dom_id + ' div.items:last div.item', el);
                    var content_pagination = $('#' + listing_dom_id + ' div.pagination', el);
                }
                else
                {
                    var content = $('div#content div.items:last div.item', el);
                    var content_pagination = $('div#content div.pagination', el);
                }
                target_items.append(content);
                target_pagination.replaceWith(content_pagination);
                $(document).trigger("onListingRefresh", [target]);
            }
        );
    });

    // Ajaxify comment pagination.
    $(document).on('click', 'div.foundry-comments-list div.pagination a', function(e){
        e.preventDefault();
        target = $(this).parents('div.foundry-comments-list:first');
        var target_items = $('div.items:last', target);
        var target_pagination = $('div.pagination', target);
        url = $(location).attr('href');
        // Strip params. Already present in href.
        url = url.split('?')[0];
        url = url + $(this).attr('href');
        $.get(
            url,
            {},
            function(data){
                // Markup contains fluff. We want only the content.
                var el = $('<div>' + data + '</div>');
                var content = $('div#content div.foundry-comments-list div.items:last div.item', el);
                target_items.append(content);
                var content = $('div#content div.foundry-comments-list div.pagination', el);
                target_pagination.replaceWith(content);
                $(document).trigger("onCommentsPaginate", [target]);
            }
        );
    });

    // Ajaxify view modifier navigation for (1) standalone listing (2) listing in a tile.
    $(document).on('click', 'div.foundry-listing div.jmbo-view-modifier div.item a', function(e){
        e.preventDefault();
        var target = $(this).parents('div.foundry-page-tile:first');
        var url = target.attr('original_url');
        if (!target.length)
        {
            target = $(this).parents('div.foundry-listing:first');
            url = $(location).attr('href');
        }
        // Strip params. Already present in href.
        url = url.split('?')[0];
        url = url + $(this).attr('href');
        $.get(
            url,
            {},
            function(data){
                if (data.search('id="content"') != -1)
                {
                    // Markup that contains fluff. We want only the content.
                    var el = $('<div>' + data + '</div>');
                    var content = $('div#content', el);
                    target.html(content.html());
                }
                else
                    target.html(data);
                $(document).trigger("onListingRefresh", [target]);
            }
        );
    });

    var _submit_intercept_common = function(sender, event, target){
        // Common functionality
        event.preventDefault();
        var url = $(sender).attr('action');
        if ((!url) || (url == '.'))
            url = target.attr('original_url');
        var data = $(sender).serialize();
        $.ajax({
            url: url,
            data: data,
            async: false,
            type: 'POST',
            cache: false,
            success: function(data){
                if (data.indexOf('{') == 0)
                {
                    var obj = $.parseJSON(data);
                    $(obj.render_target).html(obj.html);
                    // messages todo
                }
                else
                    if (data.search('id="content"') != -1)
                    {
                        // Markup that contains fluff. We want only the content.
                        var el = $('<div>' + data + '</div>');
                        var content = $('div#content', el);
                        target.html(content.html());
                    }
                    else
                        target.html(data);
            }
        })
    };

    // Intercept tile form submit for contained items (eg. a listing). The heading must be preserved.
    // An example is a tile containing a listing of polls.
    $(document).on('submit', 'div.foundry-enable-ajax .foundry-container form', function(event){
        event.stopImmediatePropagation();
        var target = $(this).parents('div.item:first');
        _submit_intercept_common(this, event, target);
    });

    // Intercept tile form submit for views with a form.
    // An example is a normal standalone form like site_contact.
    $(document).on('submit', 'div.foundry-enable-ajax form', function(event){
        var target = $(this).parents('div.foundry-enable-ajax:first');
        _submit_intercept_common(this, event, target);
    });

    // Post a comment
    $(document).on('submit', 'form.comment-form', function(event){
        event.preventDefault();
        var form = $(this);
        var url = $(this).attr('action');
        var data = $(this).serialize() + '&paginate_offset=-1';
        $.ajax({
            url: url,
            data: data,
            async: false,
            type: 'POST',
            cache: false,
            success: function(data){
                if (data.indexOf('{') == 0)
                {
                    var obj = $.parseJSON(data);
                    $('div.comment-list').html(obj.html);
                    var el = $('#id_comment');
                    el.val('');
                    $('#c'+obj.obj_id).attr('tabindex', -1).focus();
                }
                else
                    form.replaceWith(data);
            },
            complete: function(){
                // Clear in reply to in all cases
                $('#id_in_reply_to').val('');
            }
        })
    });

    // Report a comment
    $(document).on('click', 'div.foundry-comments-list a.report', function(){
        if (!window.confirm('Are you sure you want to report this?'))
            return false;

        var el = $(this);
        var url = el.attr('href');
        $.ajax({
            url: url,
            async: true,
            type: 'GET',
            cache: false,
            success: function(data){
                el.replaceWith('Reported');
            }
        });
        return false;
    });

    // Load new comments and chats
    function load_new_comments(){
        if ($.now() - last_activity_time < 30000)
            $('div.comment-list-placeholder').each(function(index){
                var el = $(this);
                var url = '/fetch-new-comments-ajax/' + el.attr('content_type_id') + '/' + el.attr('oid') + '/' + el.attr('last_comment_id') + '/';
                $.get(
                    url,
                    {},
                    function(data){
                        if (data)
                            el.replaceWith(data);
                    }
                );
            });
    }
    setInterval(load_new_comments, 30000);

    }

});
