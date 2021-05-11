odoo.define("easy_my_coop_loan_website.oe_easymy_coop_loan", function (require) {
    $(document).ready(function () {
        "use strict";
        var ajax = require("web.ajax");

        $(".oe_easymy_coop_loan").each(function () {
            var oe_easymy_coop_loan = this;
            $("#loan_issue").change(function () {
                var loan_issue_id = $("#loan_issue").val();
                ajax.jsonRpc("/subscription/get_loan_issue", "call", {
                    loan_issue_id: loan_issue_id,
                }).then(function (data) {
                    if (data !== false) {
                        $("#subscription_amount").prop(
                            "max",
                            data[loan_issue_id].maximum_amount_per_sub
                        );
                        $("#subscription_amount").prop(
                            "step",
                            data[loan_issue_id].face_value
                        );
                    }
                });
            });
            $("#loan_issue").trigger("change");
        });
    });
});
