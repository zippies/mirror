(function($) {

	$.fn.imgNotes = function(n) {
	
		if(undefined != n){
			notes = n;
		} 
	
		imgOffset = $(this).offset();

		$(notes).each(function(){
			appendnote(this);
		});	
		
		$(this).click(function(e) {
			$(".note").hide();
			var eve = e || window.event;
			var x = parseInt(eve.clientX) - parseInt(imgOffset.left);
			var y = parseInt(eve.clientY) - parseInt(imgOffset.top);

			$.get("/showcloser",{"x":x,"y":y},function(em) {
				if(em != "0"){
					$("#"+em).show();
					$("#nodeTreeView").treeview('expandAll');
					$('#nodeTreeView').treeview('selectNode',parseInt(em)-1);
				}
			})
		})
	
	} 
	
	function appendnote(note_data){
		note_left  = parseInt(imgOffset.left) + parseInt(note_data.x1);
		note_top   = parseInt(imgOffset.top) + parseInt(note_data.y1);
		note_p_top = note_top + parseInt(note_data.height)+5;
		//console.log("id:"+note_data.id+" x1:"+note_data.x1+" y1:"+note_data.y1)
		note_area_div = $("<div class='note' id='"+ note_data.id + "' ></div>").css({ left: note_left + 'px', top: note_top + 'px', width: note_data.width + 'px', height: note_data.height + 'px' });
		
		note_text_div = $('<div class="notep" >'+note_data.note+'</div>').css({ left: note_left + 'px', top: note_p_top + 'px'});
	
		$('body').append(note_area_div);
		$('body').append(note_text_div);
	}

// End the closure
})(jQuery);