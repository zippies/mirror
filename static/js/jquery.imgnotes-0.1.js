/**
 * imgnotes jQuery plugin
 * version 0.1
 *
 * Copyright (c) 2008 Dr. Tarique Sani <tarique@sanisoft.com>
 *
 * Dual licensed under the MIT (MIT-LICENSE.txt) 
 * and GPL (GPL-LICENSE.txt) licenses.
 *
 * @URL      http://www.sanisoft.com/blog/2008/05/26/img-notes-jquery-plugin/
 * @Example  example.html
 *
 **/

//Wrap in a closure
(function($) {

	$.fn.imgNotes = function(n) {
	
		if(undefined != n){
			notes = n;
		} 
	
		imgOffset = $(this).offset();
		console.log(imgOffset.left)
		console.log(imgOffset.top)
		$(notes).each(function(){
			appendnote(this);
		});	
		
		$(this).click(function(e) {
			$(".note").hide();
			var eve = e || window.event;
			var x = parseInt(eve.clientX) - parseInt(imgOffset.left);
			var y = parseInt(eve.clientY) - parseInt(imgOffset.top);
			//alert(eve.clientX+" "+imgOffset.left + " " +eve.clientY+" "+imgOffset.top+" "+"x:"+x+" "+"y:"+y)

			$.get("http://10.88.0.40:8088/showcloser",{"x":x,"y":y},function(em) {
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
		console.log("id:"+note_data.id+" x1:"+note_data.x1+" y1:"+note_data.y1)
		note_area_div = $("<div class='note' id='"+ note_data.id + "' ></div>").css({ left: note_left + 'px', top: note_top + 'px', width: note_data.width + 'px', height: note_data.height + 'px' });
		
		note_text_div = $('<div class="notep" >'+note_data.note+'</div>').css({ left: note_left + 'px', top: note_p_top + 'px'});
	
		$('body').append(note_area_div);
		$('body').append(note_text_div);
	}

// End the closure
})(jQuery);