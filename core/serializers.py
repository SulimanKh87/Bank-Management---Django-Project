# core/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User  # Import the User model
from .models import UserProfile, Customer, BankAccount, Transaction, Loan, Currency, Bank


# UserProfile Serializer
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'email', 'name', 'is_active', 'is_staff']


# Customer Serializer
class CustomerSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer()

    class Meta:
        model = Customer
        fields = ['id', 'user', 'phone', 'address']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create_user(**user_data)  # Correctly create a user
        customer = Customer.objects.create(user=user, **validated_data)
        return customer


# BankAccount Serializer
class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = ['id', 'customer', 'balance', 'is_suspended']


# Currency Serializer
class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ['id', 'code', 'exchange_rate']


# Transaction Serializer
class TransactionSerializer(serializers.ModelSerializer):
    currency = CurrencySerializer()  # Include currency details in the transaction response

    class Meta:
        model = Transaction
        fields = ['id', 'account', 'amount', 'transaction_type', 'fee', 'currency']

    def create(self, validated_data):
        account = validated_data['account']
        fee_percentage = 0.02  # Example: 2% fee for all transactions
        amount = validated_data['amount']

        # Calculate the fee
        validated_data['fee'] = amount * fee_percentage

        if validated_data['transaction_type'] == 'deposit':
            account.deposit(amount)
        elif validated_data['transaction_type'] == 'withdraw':
            account.withdraw(amount)
        elif validated_data['transaction_type'] == 'transfer':
            target_account_id = validated_data.pop('target_account_id')
            target_account = BankAccount.objects.get(id=target_account_id)
            account.transfer(amount, target_account)

        account.save()
        return super().create(validated_data)


# Loan Serializer
class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = ['id', 'customer', 'amount', 'is_repaid']

    def create(self, validated_data):
        bank = Bank.objects.first()  # Assume you have a single bank instance
        amount = validated_data['amount']

        if amount > 50000:
            raise serializers.ValidationError("Maximum loan is 50,000 NIS.")

        if bank.balance < amount:
            raise serializers.ValidationError("Bank does not have enough funds for this loan.")

        bank.grant_loan(amount)
        loan = Loan.objects.create(**validated_data)
        return loan
