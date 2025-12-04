# gemini/admin.py

import os
import json
from django.conf import settings
from django.http import JsonResponse
from django.urls import path
from django.contrib import admin
from django import forms
from .models import GeminiQuery
from . import services

@admin.register(GeminiQuery)
class GeminiQueryAdmin(admin.ModelAdmin):
    # --- Osnovna Konfiguracija Admina ---
    list_display = ('question', 'response', 'token_count', 'timestamp', 'is_integrated')
    ordering = ('-timestamp',)
    readonly_fields = ('timestamp', 'raw_response', 'client_request', 'existing_content')

    # --- Povezivanje s Našim Custom Templateima ---
    change_list_template = "admin/gemini/geminiquery/change_list.html"
    change_form_template = "admin/gemini/geminiquery/change_form.html"

    # --- DEFINICIJA NAŠIH CUSTOM URL-ova UNUTAR ADMINA ---
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('<int:object_id>/fetch-content/', self.admin_site.admin_view(self.ajax_fetch_content_view),
                 name='gemini_query_fetch_content'),
            path('<int:object_id>/push-content/', self.admin_site.admin_view(self.ajax_push_content_view),
                 name='gemini_query_push_content'),
        ]
        return my_urls + urls

    # --- METODA ZA LISTU SVIH ZAPISA ---
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}

        if '_run_ai_query' in request.POST:
            question = request.POST.get('ai_question', '').strip()
            selected_folder = request.POST.get('folder_to_read', '').strip()
            history_count = int(request.POST.get('history_value_setting'))

            if question:
                full_prompt = question
                if selected_folder:
                    folder_content = services.read_folder_contents(selected_folder)
                    full_prompt = f"Pitanje: '{question}'\n\nKontekst iz foldera '{selected_folder}':\n{folder_content}"

                ai_response, raw_resp_dict, tokens, request_payload = services.get_ai_response(full_prompt, history_count)

                GeminiQuery.objects.create(
                    question=question, response=ai_response, raw_response=raw_resp_dict,
                    token_count=tokens, client_request=request_payload
                )

                message = f"AI Query uspješno izvršen."
                if tokens is not None:
                    message += f" Potrošeno tokena: {tokens}"
                self.message_user(request, message)

        project_root = settings.BASE_DIR
        excluded_folders = {'.git', '.idea', 'venv', '__pycache__', '.venv', 'media'}
        project_folders = []
        try:
            all_items = os.listdir(project_root)
            project_folders = [item for item in all_items if
                               os.path.isdir(os.path.join(project_root, item)) and item not in excluded_folders]
        except Exception as e:
            print(f"Greška pri čitanju foldera: {e}")

        extra_context['history_count'] = int(0)
        extra_context['project_folders'] = sorted(project_folders)

        extra_context['media'] = self.media + forms.Media(
            css={'all': ('https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/css/select2.min.css',)},
            js=('admin/js/vendor/jquery/jquery.js',
                'https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/js/select2.min.js',)
        )
        return super().changelist_view(request, extra_context=extra_context)

    # --- METODA ZA DETALJNI PRIKAZ JEDNOG ZAPISA ---
    def change_form_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['media'] = self.media + forms.Media(
            css={'all': ('https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css',)},
            js=('https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js',
                'https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/autoloader/prism-autoloader.min.js',)
        )
        return super().change_form_view(request, object_id, form_url, extra_context)

    # --- NAŠI PRIVATNI AJAX VIEW-ovi ---
    def ajax_fetch_content_view(self, request, object_id=None):
        if request.method == 'POST':
            try:
                query_obj = self.get_object(request, object_id)
                if query_obj and query_obj.response:
                    existing_file_content = services.read_files_from_response(query_obj.response)
                    query_obj.existing_content = existing_file_content
                    query_obj.save()
                    return JsonResponse({'status': 'success', 'content': existing_file_content})
                else:
                    return JsonResponse({'status': 'warning', 'message': 'Nema odgovora za primjenu fetch content viow.'})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

    def ajax_push_content_view(self, request, object_id=None):
        if request.method == 'POST':
            try:
                query_obj = self.get_object(request, object_id)
                if query_obj and query_obj.response:
                    report = services.apply_code_to_files(query_obj.response)
                    if "GREŠKA" not in report:
                        query_obj.is_integrated = True
                        query_obj.save()
                    return JsonResponse({'status': 'success', 'report': report})
                else:
                    return JsonResponse({'status': 'warning', 'message': 'Nema odgovora za primjenu push content view.'})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)