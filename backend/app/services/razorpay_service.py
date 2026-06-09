import hashlib
import hmac
import os
import uuid

from dotenv import load_dotenv

load_dotenv()

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "rzp_test_stub")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "test_secret_stub")
RAZORPAY_TEST_MODE = os.getenv("RAZORPAY_TEST_MODE", "true").lower() == "true"


def create_order(invoice_id: int, amount: float, resident_name: str, flat_number: str):
    amount_paise = int(round(amount * 100))
    description = f"Maintenance - Flat {flat_number} ({resident_name})"

    if not RAZORPAY_TEST_MODE and RAZORPAY_KEY_ID.startswith("rzp_"):
        try:
            import razorpay

            client = razorpay.Client(
                auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET)
            )

            order = client.order.create({
                "amount": amount_paise,
                "currency": "INR",
                "receipt": f"inv_{invoice_id}_{uuid.uuid4().hex[:8]}",
                "notes": {
                    "invoice_id": str(invoice_id),
                    "flat_number": flat_number,
                    "resident_name": resident_name,
                }
            })

            return {
                "success": True,
                "order_id": order["id"],
                "amount": amount_paise,
                "currency": "INR",
                "key_id": RAZORPAY_KEY_ID,
                "test_mode": False,
                "description": description,
                "invoice_id": invoice_id,
            }

        except Exception as ex:
            return {
                "success": False,
                "message": f"Razorpay order failed: {str(ex)}"
            }

    order_id = f"order_{uuid.uuid4().hex[:16]}"

    return {
        "success": True,
        "order_id": order_id,
        "amount": amount_paise,
        "currency": "INR",
        "key_id": RAZORPAY_KEY_ID,
        "test_mode": True,
        "description": description,
        "invoice_id": invoice_id,
    }


def verify_signature(order_id: str, payment_id: str, signature: str) -> bool:
    if RAZORPAY_TEST_MODE:
        return (
            signature.startswith("test_sig_") or
            signature == "stub" or
            len(signature) > 10
        )

    body = f"{order_id}|{payment_id}"
    expected = hmac.new(
        RAZORPAY_KEY_SECRET.encode("utf-8"),
        body.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected, signature)


def generate_test_signature(order_id: str, payment_id: str) -> str:
    if RAZORPAY_TEST_MODE:
        return f"test_sig_{order_id}_{payment_id}"
    return ""
