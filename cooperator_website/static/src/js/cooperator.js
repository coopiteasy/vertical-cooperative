odoo.define("cooperator.oe_cooperator", function (require) {
    "use strict";
    $(document).ready(function () {
        var ajax = require("web.ajax");

        $(".oe_cooperator").each(function () {
            var oe_cooperator = this;

            $("#share_product_id").change(function () {
                var share_product_id = $("#share_product_id").val();
                ajax.jsonRpc("/subscription/get_share_product", "call", {
                    share_product_id: share_product_id,
                }).then(function (data) {
                    $("#share_price").text(data[share_product_id].list_price);
                    $("#ordered_parts").val(data[share_product_id].min_qty);
                    if (data[share_product_id].force_min_qty === true) {
                        $("#ordered_parts").data("min", data[share_product_id].min_qty);
                    }
                    $("#ordered_parts").change();
                    var $share_price = $("#share_price").text();
                    $('input[name="total_parts"]').val(
                        $("#ordered_parts").val() * $share_price
                    );
                    $('input[name="total_parts"]').change();
                });
            });

            $(oe_cooperator).on("change", "#ordered_parts", function (event) {
                var $share_price = $("#share_price").text();
                var $link = $(event.currentTarget);
                var quantity = $link[0].value;
                var total_part = quantity * $share_price;
                $("#total_parts").val(total_part);
                return false;
            });

            $(oe_cooperator).on("focusout", "input.js_quantity", function () {
                $("a.js_add_cart_json").trigger("click");
            });

            $("#share_product_id").trigger("change");
        });
    });
});
