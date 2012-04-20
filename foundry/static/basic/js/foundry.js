$(document).ready(function(){

    // Ajaxify tile paging, view modifier
    $('div.foundry-enable-ajax div.pagination a, div.foundry-enable-ajax div.jmbo-view-modifier a').live('click', function(e){
        e.preventDefault();
        var target = $(this).parents('div.foundry-enable-ajax:first');
        var url = target.attr('original_url');
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
    $('div.foundry-enable-ajax .foundry-container form').live('submit', function(event){
        event.stopImmediatePropagation();
        var target = $(this).parents('div.item:first');
        _submit_intercept_common(this, event, target);
    });

    // Intercept tile form submit for views with a form. 
    // An example is a normal standalone form like site_contact.
    $('div.foundry-enable-ajax form').live('submit', function(event){
        var target = $(this).parents('div.foundry-enable-ajax:first');
        _submit_intercept_common(this, event, target);
    });

    // Load new comments and chats
    function load_new_comments(){
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

});
