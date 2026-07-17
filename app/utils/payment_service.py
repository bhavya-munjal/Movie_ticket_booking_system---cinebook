"""
Payment Service - Mock Implementation
To integrate real payment: replace process_payment() internals with Razorpay/Stripe SDK.
All payment logic routes through this single file.
"""
import uuid
from datetime import datetime
from dataclasses import dataclass

@dataclass
class PaymentResult:
    success: bool
    transaction_id: str
    message: str
    amount: float

def process_payment(user_id: int, booking_ref: str, amount: float, method: str = "card") -> PaymentResult:
    """
    MOCK: Replace this with real payment gateway call.
    Example for Razorpay:
        import razorpay
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY, settings.RAZORPAY_SECRET))
        order = client.order.create({"amount": int(amount*100), "currency": "INR"})
        ...
    """
    transaction_id = f"TXN{uuid.uuid4().hex[:12].upper()}"

    print("\n" + "="*50)
    print(f"💳 PAYMENT PROCESSED [{datetime.now().strftime('%H:%M:%S')}]")
    print(f"Booking Ref  : {booking_ref}")
    print(f"User ID      : {user_id}")
    print(f"Amount       : ₹{amount:.2f}")
    print(f"Method       : {method}")
    print(f"Transaction  : {transaction_id}")
    print(f"Status       : SUCCESS (mock)")
    print("="*50 + "\n")

    return PaymentResult(
        success=True,
        transaction_id=transaction_id,
        message="Payment successful",
        amount=amount
    )

def refund_payment(transaction_id: str, amount: float) -> PaymentResult:
    """
    MOCK: Replace with real refund API call.
    """
    refund_id = f"RFD{uuid.uuid4().hex[:10].upper()}"
    print(f"\n💰 REFUND INITIATED: {refund_id} for TXN {transaction_id} — ₹{amount:.2f}\n")
    return PaymentResult(success=True, transaction_id=refund_id, message="Refund initiated", amount=amount)
