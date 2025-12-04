# gemini/models.py

from django.db import models


class GeminiQuery(models.Model):
    # Core data
    question = models.TextField(verbose_name="Korisnikovo Pitanje")
    response = models.TextField(verbose_name="Geminijev Odgovor")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Vrijeme Zapisa")

    # Metadata from API
    raw_response = models.JSONField(null=True, blank=True, verbose_name="Sirovi JSON Odgovor")
    token_count = models.PositiveIntegerField(null=True, blank=True, verbose_name="Broj Tokena")
    client_request = models.JSONField(null=True, blank=True, verbose_name="Poslani API Request")

    # Data from file operations
    existing_content = models.TextField(null=True, blank=True, verbose_name="Zatečeni Sadržaj Fajlova")

    # --- NOVO POLJE ZA STATUS ---
    is_integrated = models.BooleanField(default=False, verbose_name="Promjene Primijenjene")

    # -----------------------------

    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = "Gemini Zapisi"

    def __str__(self):
        return self.question[:80]