$(document).ready(function(){

    // Ajaxify tile paging
    $('div.foundry-enable-ajax div.pagination a').live('click', function(e){
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

    // Intercept tile form submit
    $('div.foundry-enable-ajax form').live('submit', function(event){
        event.preventDefault();
        var target = $(this).parents('div.foundry-enable-ajax:first');
        var url = $(this).attr('action');
        if ((!url) || (url == '.'))
            url = target.attr('original_url');
        var data = $(this).serialize();
        $.ajax({
            url: url,
            data: data,
            async: false,
            type: 'POST',
            cache: false,                    
            success: function(data){
                //alert(data);
                if (data.indexOf('{') == 0)
                {
                    var obj = $.parseJSON(data);
                    $('#edit-dialog').dialog('close');
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
        });
    });

});
