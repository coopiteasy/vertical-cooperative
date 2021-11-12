odoo.define("easy_my_coop.oe_easymy_coop", function (require) {
    $(document).ready(function () {
        "use strict";
        var ajax = require("web.ajax");

        $(".oe_easymy_coop").each(function () {
            var oe_easymy_coop = this;

            $("#share_product_id").change(function () {
                var share_product_id = $("#share_product_id").val();
                ajax.jsonRpc("/subscription/get_share_product", "call", {
                    share_product_id: share_product_id,
                }).then(function (data) {
                    $("#share_price").text(data[share_product_id].list_price);
                    $("#ordered_parts").val(data[share_product_id].min_qty);
                    if (data[share_product_id].force_min_qty == true) {
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

            $(oe_easymy_coop).on("change", "#ordered_parts", function (ev) {
                var $share_price = $("#share_price").text();
                var $link = $(ev.currentTarget);
                var quantity = $link[0].value;
                var total_part = quantity * $share_price;
                $("#total_parts").val(total_part);
                return false;
            });

            $(oe_easymy_coop).on("focusout", "input.js_quantity", function (ev) {
                $("a.js_add_cart_json").trigger("click");
            });

            $("#share_product_id").trigger("change");

            $("[name='birthdate']").inputmask();
        });
    });
});
