function init_create_user() {
	$("#createUser").accordion({
		collapsible: true,
		header: "h5",
		active: false,
		animate: 120
	});
	//----
	// enable create button
	$("#id_username").focusin(function () {
		//if ($(this).val()) {
		$("input:submit").attr('disabled', false);
		//}
	});
	//----
	var options = {
		beforeSubmit: pre_create, // pre-submit callback 
		success: post_create, // post-submit callback 
		dataType: 'json' // 'xml', 'script', or 'json' (expected server response type) 
	};
	$("#createUserForm").submit(function () {
		$(this).ajaxSubmit(options);
		return false;
	});
}

// pre-submit callback 

function pre_create(formData, jqForm, options) {
	show_message("");
	return true;
}

// post-submit callback 

function post_create(json_obj, statusText, xhr, $form) {
	//alert('status: ' + statusText + '\n\nresponseText: \n' + json_obj.non_existed);
	if (!json_obj.success) {
		show_upload_message(json_obj.reason);
	} else {
		// display success message; add row to table
		show_upload_message("User created successfully!");
		clear_create_user_form();

//		var row = json_obj.newfile; //,	$row = $(row), resort = true;
//		$('#userTable')
//			.find('tbody').prepend(row)
//			.trigger('update');
			//.trigger('sorton',[ [[5,1],] ]); //descending asset id
			//.trigger('addRows', [row, resort]);
	}
}

function show_message(message) {
	$('#message').html(message);
}

function clear_create_user_form() {
	$('#id_username').val("");
	$("input:submit").attr('disabled', true);
}
