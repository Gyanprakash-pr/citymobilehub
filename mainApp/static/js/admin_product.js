(function() {
    document.addEventListener("DOMContentLoaded", function() {
        const basepriceField = document.getElementById("id_baseprice");
        const discountField = document.getElementById("id_discount");
        const finalpriceField = document.getElementById("id_finalprice");

        function calculateFinalPrice() {
            const baseprice = parseFloat(basepriceField.value) || 0;
            const discount = parseFloat(discountField.value) || 0;
            
            if (baseprice >= 0 && discount >= 0) {
                // Calculate discount as a percentage
                const finalprice = baseprice - (baseprice * discount / 100);
                finalpriceField.value = Math.round(finalprice);
            }
        }

        if (basepriceField && discountField && finalpriceField) {
            basepriceField.addEventListener("input", calculateFinalPrice);
            discountField.addEventListener("input", calculateFinalPrice);
        }
    });
})();
