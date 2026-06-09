export function loadRazorpayScript() {

    return new Promise((resolve, reject) => {

        if (window.Razorpay) {
            resolve();
            return;
        }

        const script = document.createElement("script");
        script.src = "https://checkout.razorpay.com/v1/checkout.js";
        script.onload = () => resolve();
        script.onerror = () =>
            reject(new Error("Failed to load Razorpay checkout"));
        document.body.appendChild(script);
    });
}

export async function payInvoice(invoiceId, api) {

    const orderRes = await api.post("/payment/create-order", {
        invoice_id: invoiceId
    });

    const order = orderRes.data;

    if (order.success === false) {
        throw new Error(order.message || "Unable to create payment order");
    }

    if (order.test_mode) {
        const testPaymentId = `pay_test_${Date.now()}`;
        const verifyRes = await api.post("/payment/verify", {
            invoice_id: invoiceId,
            order_id: order.order_id,
            payment_id: testPaymentId,
            signature: `test_sig_${order.order_id}_${testPaymentId}`
        });

        if (!verifyRes.data.success) {
            throw new Error(verifyRes.data.message || "Payment failed");
        }

        return verifyRes.data;
    }

    await loadRazorpayScript();

    return new Promise((resolve, reject) => {

        const options = {
            key: order.key_id,
            amount: order.amount,
            currency: order.currency,
            name: "Society Management",
            description: order.description,
            order_id: order.order_id,
            theme: { color: "#0d6efd" },
            handler: async function (response) {

                try {

                    const verifyRes = await api.post("/payment/verify", {
                        invoice_id: invoiceId,
                        order_id: response.razorpay_order_id,
                        payment_id: response.razorpay_payment_id,
                        signature: response.razorpay_signature
                    });

                    if (!verifyRes.data.success) {
                        reject(
                            new Error(
                                verifyRes.data.message || "Verification failed"
                            )
                        );
                        return;
                    }

                    resolve(verifyRes.data);

                } catch (err) {
                    reject(err);
                }
            },
            modal: {
                ondismiss: function () {
                    reject(new Error("Payment cancelled"));
                }
            }
        };

        const rzp = new window.Razorpay(options);
        rzp.open();
    });
}
