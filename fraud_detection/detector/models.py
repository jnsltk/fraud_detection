from django.db import models
from django.utils.timezone import now  # Import now for default timestamps
from django.contrib.auth.models import User


class Transaction(models.Model):
    transaction_id = models.CharField(max_length=20, primary_key=True)
    customer_id = models.CharField(max_length=20)
    card_number = models.CharField(max_length=20)
    timestamp = models.DateTimeField()
    merchant_category = models.CharField(max_length=50, null=True, blank=True)
    merchant_type = models.CharField(max_length=50, null=True, blank=True)
    merchant = models.CharField(max_length=100, null=True, blank=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    city_size = models.CharField(max_length=20, null=True, blank=True)
    card_type = models.CharField(max_length=50, null=True, blank=True)
    card_present = models.BooleanField(null=True)
    device = models.CharField(max_length=50, null=True, blank=True)
    channel = models.CharField(max_length=20, null=True, blank=True)
    device_fingerprint = models.CharField(max_length=100, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True, protocol='both')
    distance_from_home = models.BooleanField(null=True)
    high_risk_merchant = models.BooleanField(null=True)
    transaction_hour = models.SmallIntegerField()
    weekend_transaction = models.BooleanField(null=True)
    v_num_transactions = models.DecimalField(max_digits=50, decimal_places=0, null=True, blank=True)
    v_total_amount = models.DecimalField(max_digits=50, decimal_places=20, null=True, blank=True)
    v_unique_merchants = models.DecimalField(max_digits=50, decimal_places=0, null=True, blank=True)
    v_unique_countries = models.DecimalField(max_digits=50, decimal_places=0, null=True, blank=True)
    v_max_single_amount = models.DecimalField(max_digits=50, decimal_places=20, null=True, blank=True)
    is_fraud = models.BooleanField()
    version_date = models.DateTimeField(default=now) # Field for versioning


class FraudDetectionModel(models.Model):
    version = models.CharField(max_length=50)
    date_created = models.DateField()
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='fraud_models')
    dataset_size = models.IntegerField()
    training_data_start_date = models.DateField()
    training_data_end_date = models.DateField()
    score = models.DecimalField(max_digits=10, decimal_places=2)
    detailed_performance = models.JSONField()
    metadata = models.JSONField()
    model_file = models.BinaryField()
    is_deployed = models.BooleanField()

