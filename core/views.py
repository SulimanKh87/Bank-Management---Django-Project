# core/views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from .models import UserProfile, Customer, BankAccount, Transaction, Loan, Bank
from .serializers import (
    CustomerSerializer,
    BankAccountSerializer,
    TransactionSerializer,
    LoanSerializer,
    UserProfileSerializer
)


# Customer ViewSet
class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


# Bank Account ViewSet
class BankAccountViewSet(viewsets.ModelViewSet):
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):  # Include request and pk for consistency
        account = self.get_object()
        account.close()  # Close account logic in the model
        return Response({"message": "Account closed successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def deposit(self, request, pk=None):  # Include pk for consistency
        account = self.get_object()
        amount = request.data.get('amount')
        account.deposit(amount)  # Deposit logic in the model
        return Response({"message": "Deposit successful."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def withdraw(self, request, pk=None):  # Include pk for consistency
        account = self.get_object()
        amount = request.data.get('amount')
        account.withdraw(amount)  # Withdraw logic in the model
        return Response({"message": "Withdrawal successful."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def get_balance(self, request, pk=None):  # Include pk for consistency
        account = self.get_object()
        return Response({"balance": account.balance}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def transfer(self, request):
        from_account_id = request.data.get('from_account_id')
        to_account_id = request.data.get('to_account_id')
        amount = request.data.get('amount')

        from_account = BankAccount.objects.get(pk=from_account_id)
        to_account = BankAccount.objects.get(pk=to_account_id)

        from_account.withdraw(amount)
        to_account.deposit(amount)

        return Response({"message": "Transfer successful."}, status=status.HTTP_200_OK)


# Transaction ViewSet
class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Transaction.objects.filter(account__customer__user=user)


# Loan ViewSet
class LoanViewSet(viewsets.ModelViewSet):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        amount = request.data.get('amount')
        bank = Bank.objects.first()  # Assuming only one bank instance

        if bank.balance < amount:
            return Response({"error": "Bank does not have enough funds for this loan."},
                            status=status.HTTP_400_BAD_REQUEST)

        bank.grant_loan(amount)  # Grant loan logic in the model
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def repay(self, request, pk=None):  # Include pk parameter for consistency
        loan = self.get_object()
        repayment_amount = request.data.get('repayment_amount')
        loan.repay(repayment_amount)  # Repay logic in the model
        return Response({"message": "Loan repayment successful."}, status=status.HTTP_200_OK)

    @staticmethod
    def get_customer_loans(customer_id):
        loans = Loan.objects.filter(customer__id=customer_id)
        serializer = LoanSerializer(loans, many=True)
        return Response(serializer.data)


# Loan Repayment ViewSet
class LoanRepaymentViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request, pk=None):
        loan = Loan.objects.get(pk=pk)
        repayment_amount = request.data.get('repayment_amount')

        try:
            loan.repay(repayment_amount)
            return Response({"message": "Loan repayment successful."}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# User Profile ViewSet
class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
