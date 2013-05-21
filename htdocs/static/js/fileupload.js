function init_upload() {
	$("#fileUpload").accordion({
		collapsible: true,
		header: "h5",
		active: false,
		animate: 120
	});
	//----
	// enable upload button
	$("input:file").change(function () {
		if ($(this).val()) {
			$("input:submit").attr('disabled', false);
		}
	});
	//----
	var options = {
		beforeSubmit: pre_upload, // pre-submit callback 
		success: post_upload, // post-submit callback 
		dataType: 'json' // 'xml', 'script', or 'json' (expected server response type) 
	};
	$("#uploadForm").submit(function () {
		$(this).ajaxSubmit(options);
		return false;
	});
}

// pre-submit callback 

function pre_upload(formData, jqForm, options) {
	// formData is an array; here we use $.param to convert it to a string to display it 
	// but the form plugin does this for you automatically when it submits the data 
	//var queryString = $.param(formData);
	// jqForm is a jQuery object encapsulating the form element.  To access the 
	// DOM element for the form do this: 
	// var formElement = jqForm[0]; 

	//alert('About to submit: \n\n' + queryString); 

	show_upload_message("");
	// do validation
	return true;
}

// post-submit callback 

function post_upload(json_obj, statusText, xhr, $form) {
	//alert('status: ' + statusText + '\n\nresponseText: \n' + json_obj.non_existed);
	if (!json_obj.non_existed) {
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
							$.post("upload/confirm/", {
								overwrite: true,
								aid: json_obj.aid,
								new_mime_type: json_obj.new_mime_type,
								new_nice_type: json_obj.new_nice_type,
								new_keywords: json_obj.new_keywords
							});
							$(this).dialog("close");
							show_upload_message("File uploaded successfully!");
							clear_upload_form();
						},
						Cancel: function () {
							$.post("upload/confirm/", {
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
			show_upload_message("Existed file! You don't have permission to overwrite. Please choose another title.");
		}

	} else {
		// display success message; add row to table
		show_upload_message("File uploaded successfully!");
		clear_upload_form();

		var row = json_obj.newfile; //,	$row = $(row), resort = true;
		$('#fileTable')
			.find('tbody').prepend(row)
			.trigger('update');
			//.trigger('sorton',[ [[5,1],] ]); //descending asset id
			//.trigger('addRows', [row, resort]);
	}
}

function show_upload_message(message) {
	$('#message').html(message);
}

function clear_upload_form() {
	$('#id_title').val("");
	$('#id_file').val("");
	$('#id_tags').val("");
	$("input:submit").attr('disabled', true);
}