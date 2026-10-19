from models import TestCase

# Format: (ticket text, expected category, expected priority)
ticket_list = [
    # --- your original 10 ---
    ("I was charged twice for my subscription this month, please fix urgently!", "billing", "high"),
    ("The app crashes every time I open the settings page.", "technical", "high"),
    ("Do you offer a discount for students?", "general", "low"),
    ("How do I change the email address on my invoices?", "billing", "low"),
    ("I cannot log in, it says my password is invalid even after a reset.", "technical", "high"),
    ("What are your support hours on weekends?", "general", "low"),
    ("My refund from last month has still not arrived.", "billing", "low"),
    ("The export to PDF button does nothing when I click it.", "technical", "low"),
    ("Our whole team is locked out and we have a client demo in one hour!", "technical", "high"),
    ("Can you send me a copy of your terms of service?", "general", "low"),
    # --- 20 new candidates (review the labels!) ---
    ("I was charged $500 instead of $50 and my account is overdrawn, please fix this today!", "billing", "high"),
    ("Someone made an unauthorized purchase on my account and I need it reversed immediately.", "billing", "high"),
    ("Can I get a PDF copy of last month's invoice?", "billing", "low"),
    ("How do I update the credit card on file for next month's payment?", "billing", "low"),
    ("Can I switch from monthly to yearly billing?", "billing", "low"),
    ("The website is completely down for all our users and we are losing sales!", "technical", "high"),
    ("All my data disappeared after the latest update, I urgently need it back!", "technical", "high"),
    ("The dark mode toggle does not remember my choice after I restart the app.", "technical", "low"),
    ("How do I enable two-factor authentication on my account?", "technical", "low"),
    ("The notification sound is too quiet on my phone.", "technical", "low"),
    ("The API returns error 500 on every request since this morning and our production app is down!", "technical", "high"),
    ("Where can I find your privacy policy?", "general", "low"),
    ("Do you have a mobile app for Android?", "general", "low"),
    ("Which languages does your support team speak?", "general", "low"),
    ("I would like to suggest a new feature for the dashboard.", "general", "low"),
    ("Do you have a partner program for resellers?", "general", "low"),
    ("Where is your company headquartered?", "general", "low"),
    ("Is there a user guide I can download for beginners?", "general", "low"),
    ("Do you plan to open an office in Europe?", "general", "low"),
    ("I am a journalist and would like to contact your press team.", "general", "low"),
]

cases = []
number = 1
for ticket_text, category, priority in ticket_list:
    case = TestCase(
        case_id="ticket_" + str(number),
        question=ticket_text,
        rules={"expected_category": category, "expected_priority": priority},
    )
    cases.append(case)
    number = number + 1