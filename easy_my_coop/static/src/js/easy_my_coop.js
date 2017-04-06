odoo.define('easy_my_coop.oe_easymy_coop', function (require) {
$(document).ready(function () {
	"use strict";
	var ajax = require('web.ajax');
	
	$('.oe_easymy_coop').each(function () {
	    var oe_easymy_coop = this;
	    
	    $('#share_product_id').change(function () {
	    	var share_product_id = $("#share_product_id").val();
	    	ajax.jsonRpc("/subscription/get_share_product", 'call', {
				'share_product_id': share_product_id
	  		 })
	  		.then(function (data) {
				$('#share_price').text(data[share_product_id].list_price);
				$('input.js_quantity').val(data[share_product_id].min_qty);
				if(data[share_product_id].force_min_qty == true){
					$('input.js_quantity').data("min",data[share_product_id].min_qty);
				}
				$('input.js_quantity').change();
				var $share_price = $('#share_price').text()
				$('input[name="total_parts"]').val($('input.js_quantity').val()*$share_price);
				$('input[name="total_parts"]').change();
	        });
	    });
	    
	    $(oe_easymy_coop).on('click', 'a.js_add_cart_json', function (ev) {
	        var $share_price = $('#share_price').text()
	        var $link = $(ev.currentTarget);
	        var $input = $link.parent().parent().find("input");
	        var $input_total = $("div").find(".total");
	        var min = parseFloat($input.data("min") || 1);
	        var amount_max = parseFloat($('input[name="total_parts"]').data("max"));
	        var quantity = ($link.has(".fa-minus").length ? -1 : 1) + parseFloat($input.val(),10);
	        var total_part = quantity * $share_price;
	        var quantity_max = amount_max / $share_price;
	        $input.val(quantity > min ? (total_part <= amount_max ? quantity : quantity_max) : min);
	        $input.change();
	        $('input[name="total_parts"]').val($input.val()*$share_price);
	        return false;
	    });
	    
	    $(oe_easymy_coop).on('focusout', 'input.js_quantity', function (ev) {
	    	$('a.js_add_cart_json').trigger('click');
	    });
	    
	    $('#share_product_id').trigger('change');
	    
	    $("[name='birthdate']").inputmask();
	});
});
});