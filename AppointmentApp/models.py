from django.db import models
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from django.utils import timezone


class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "En attente"
        CONFIRMED = "CONFIRMED", "Confirmé"
        CANCELLED = "CANCELLED", "Annulé"

    reason = models.TextField()
    appointment_date = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=9, choices=Status.choices,
        default=Status.PENDING
    )
    prescription = models.FileField(
        upload_to="prescriptions/", blank=True,
        validators=[FileExtensionValidator(["pdf"])]
    )
    doctor = models.ForeignKey(
        "AccountApp.Doctor", on_delete=models.CASCADE
    )
    patient = models.ForeignKey(
        "AccountApp.Patient", on_delete=models.CASCADE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['doctor', 'appointment_date'],
                name='unique_doctor_appointment'
            )
        ]
        ordering = ['appointment_date']

    def clean(self):
        super().clean()
        modified_date = self._state.adding or (
            not Appointment.objects.filter(
                pk=self.pk,
                appointment_date=self.appointment_date,
            ).exists()
        )
        if self.appointment_date and modified_date and (
            self.appointment_date <= timezone.now()
        ):
            raise ValidationError(
                "Appointment date cannot be in the past."
            )
    

    def __str__(self):
        return f"{self.patient} - {self.doctor} ({self.appointment_date:%d/%m/%Y %H:%M})"