$.ajaxSetup({
    beforeSend: function (xhr, settings) {
        function getCookie(name) {
            var cookieValue = null;
            if (document.cookie && document.cookie != '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = jQuery.trim(cookies[i]);
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) == (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
        if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
            // Only send the token to relative URLs i.e. locally.
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    }
});
 // pre-submit callback 

function showRequest(formData, jqForm, options) {
    // formData is an array; here we use $.param to convert it to a string to display it 
    // but the form plugin does this for you automatically when it submits the data 
    var queryString = $.param(formData);

    // jqForm is a jQuery object encapsulating the form element.  To access the 
    // DOM element for the form do this: 
    // var formElement = jqForm[0]; 

    //alert('About to submit: \n\n' + queryString); 

    // do validation
    return true;
}

 // post-submit callback 

function showResponse(json_obj, statusText, xhr, $form) {
    //alert('status: ' + statusText + '\n\nresponseText: \n' + json_obj.is_success);
    if (!json_obj.is_success) {
        // ask to overwrite
		if (json_obj.is_existed_owner) { //only ask to overwrite if current user is owner of the existed file
	        show_upload_message("Existed file!");
			$(function () {
				$("#dialog-confirm").dialog({
					resizable: false,
					height: 180,
					model: true,
					buttons: {
						"Overwrite": function () {
							$.post("{% url 'dac.uploader.views.confirm_upload_file' %}", {
								overwrite: true,
								aid: json_obj.aid
							});
							$(this).dialog("close");
							show_upload_message("File uploaded successfully!");
							clear_upload_form();
						},
						Cancel: function () {
							$.post("{% url 'dac.uploader.views.confirm_upload_file' %}", {
								overwrite: false,
								aid: json_obj.aid
							});
							$(this).dialog("close");
							show_upload_message("Canceled!");
						}
					}
            	});
        	});
		} else {
	        show_upload_message("Existed file! You don't have permission to overwrite.");
		}

    } else {
        // display success message; add row to table
        show_upload_message("File uploaded successfully!");
		clear_upload_form();

        var row = json_obj.newfile; //,	$row = $(row), resort = true;
        $('#fileTable')
        .find('tbody').prepend(row)
		.trigger('update');
        //.trigger('addRows', [row, resort]);
        //.trigger('sorton',[ [[5,1],] ]); //descending asset id
    }
}

function show_upload_message(message) {
    document.getElementById("message").innerHTML = message;
}
function clear_upload_form() {
	document.getElementById('id_title').value = "";
	document.getElementById('id_file').value = "";
	document.getElementById('id_tags').value = "";
    $("input:submit").attr('disabled', true);
}