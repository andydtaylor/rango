/**
 * Created by admin on 17/02/2014.
 */

$(document).ready(function() {


	$('#likes').click(function(){
	        var catid;
	        catid = $(this).attr("data-catid");
	         $.get('/rango/like_category/', {category_id: catid}, function(wibble){
	                   $('#like_count').html(wibble);
	                   $('#likes').hide();
	               });
	    });

    $('#suggestion').keyup(function(){
        var query;
        query = $(this).val();
        $.get('/rango/suggest_category/', {suggestion: query}, function(data){
         $('#cats').html(data);
                    });
        });

    $('.rango-add').click(function(){
        var data_cat_id = $(this).attr("data-catid");
        var data_title = $(this).attr("data-title");
        var data_url = $(this).attr("data-url");
        var me = $(this);
        $.get('/rango/auto_add_page/', {category_id: data_cat_id, url: data_url, title: data_title}, function(data){
            $('#page_updates').html(data);
            me.hide();
                    });
        });




});




