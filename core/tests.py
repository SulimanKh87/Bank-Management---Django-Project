from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from .models import BankAccount, Customer, Loan


class CustomerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.customer = Customer.objects.create(user=self.user, phone="1234567890", address="123 Street")

    def test_customer_creation(self):
        self.assertEqual(self.customer.phone, "1234567890")
        self.assertEqual(self.customer.address, "123 Street")


class BankAccountTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.customer = Customer.objects.create(user=self.user, phone="1234567890", address="123 Street")
        self.account = BankAccount.objects.create(customer=self.customer)

    def test_create_bank_account(self):
        self.assertEqual(self.account.balance, 0)

    def test_withdraw_exceeding_limit(self):
        self.account.balance = 500
        self.account.save()
        with self.assertRaises(ValidationError):
            self.account.withdraw(2000)

    def test_deposit(self):
        self.account.deposit(300)
        self.assertEqual(self.account.balance, 300)

    def test_withdraw_success(self):
        self.account.balance = 500
        self.account.save()
        self.account.withdraw(200)
        self.assertEqual(self.account.balance, 300)


class LoanTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.customer = Customer.objects.create(user=self.user, phone="1234567890", address="123 Street")
        self.loan = Loan.objects.create(customer=self.customer, amount=1000)

    def test_create_loan(self):
        self.assertEqual(self.loan.amount, 1000)
        self.assertEqual(self.loan.customer, self.customer)

    def test_repay_loan(self):
        self.loan.repay(500)
        self.assertEqual(self.loan.amount, 500)  # Adjust based on your Loan model's repay method logic

# Add more tests as needed...
