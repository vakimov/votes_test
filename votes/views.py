# -*- coding: utf-8 -*-
import hashlib
from datetime import timedelta

from django import forms
from django.http import HttpResponseRedirect, Http404
from django.views.generic import FormView, ListView, CreateView, TemplateView
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils import timezone

from .models import Voting, Choice, VotingDelay
from .translit import translit


class SignUpForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control'}),
            'next': forms.HiddenInput(),
        }

    password_confirm = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    next = forms.CharField(required=False)

    def clean_password_confirm(self):
        password = self.cleaned_data['password']
        password_confirm = self.cleaned_data['password_confirm']
        if password != password_confirm:
            raise forms.ValidationError('Пароли не совпадают')


class SignUpView(FormView):
    form_class = SignUpForm
    template_name = 'votes/signup.html'
    
    def form_valid(self, form):
        credentials = {
            'username': form.instance.username,
            'password': form.instance.password,
        }
        user = User.objects.create_user(**credentials)
        user = authenticate(**credentials)
        login(self.request, user)
        return HttpResponseRedirect(form.cleaned_data['next'] or '/')

    def get_context_data(self, **kwargs):
        context_data = super(SignUpView, self).get_context_data(**kwargs)
        if self.request.GET.get('next'):
            context_data['next'] = self.request.GET['next']
        return context_data


class VotingListView(ListView):
    model = Voting
    title = 'Голосования'
    template_name = 'votes/voting_list.html'
    ordering = '-datetime'


class UsersVotingListView(VotingListView):
    model = Voting
    title = 'Мои голосования'
    template_name = 'votes/users_voting_list.html'

    def get_queryset(self):
        queryset = super(UsersVotingListView, self).get_queryset()
        return queryset.filter(user=self.request.user)


class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['description']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control'}),
        }
        
    def is_valid(self):
        return super(ChoiceForm, self).is_valid()

    def full_clean(self):
        # self.instance.order = self.prefix
        return super(ChoiceForm, self).full_clean()


_ChoiceFormSet = forms.inlineformset_factory(Voting, Choice, form=ChoiceForm, fields=('description',))


class ChoiceFormSet(_ChoiceFormSet):
    def clean(self):
        cleaned_data = super(ChoiceFormSet, self).clean()
        descriptions = {}
        for form in self.forms:
            description = form.cleaned_data.get('description')
            if description:
                if descriptions.get(description):
                    raise forms.ValidationError('Варианты не должны повторятся')
                descriptions[description] = True
        if len(descriptions) < 2:
            raise forms.ValidationError('Должно быть как минимум два варианта')
        return cleaned_data

    def add_fields(self, form, index):
        super(ChoiceFormSet, self).add_fields(form, index)
        form.instance.order = int(index)


class VotingForm(forms.ModelForm):
    class Meta:
        model = Voting
        fields = ['slug', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_description(self):
        return self.cleaned_data.get('description', '').strip()

    def clean_slug(self):
        slug = self.cleaned_data['slug']
        if not slug:
            slug = translit(self.data['description'])
            slug = slug[:min(20, len(slug))]
            slug = slug if slug else hashlib.md5(slug.encode('utf-8')).hexdigest()[:8]

            def update_slug(slug_root, n=0):
                s = slug_root + (('_%s' % n) if n > 0 else '')
                if Voting.objects.filter(slug=s).count() > 0:
                    return update_slug(slug_root, n+1)
                return s

            slug = update_slug(slug)
        return slug


class VotingAddView(CreateView):
    model = Voting
    form_class = VotingForm
    template_name = 'votes/voting_add.html'
    success_url = reverse_lazy('votes_voting_list')

    def get(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        choices_formset = ChoiceFormSet()
        return self.render_to_response(
            self.get_context_data(
                form=form,
                choices_formset=choices_formset,
            )
        )

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        form.instance.user = self.request.user
        form.instance.datetime = timezone.now()
        choices_formset = ChoiceFormSet(self.request.POST)
        if (form.is_valid() and choices_formset.is_valid() and
            choices_formset.is_valid()):
            return self.form_valid(form, choices_formset)
        else:
            return self.form_invalid(form, choices_formset)

    def form_valid(self, form, choices_formset):
        self.object = form.save()
        choices_formset.instance = self.object
        choices_formset.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, choices_formset):
        return self.render_to_response(
            self.get_context_data(form=form,
                                  choices_formset=choices_formset))


class VotingMixin(object):

    _voting = None

    @property
    def voting(self):
        if not self._voting:
            self._voting = Voting.objects.get(slug=self.kwargs['slug'])
        return self._voting

    def get_voting_delay(self):
        try:
            return VotingDelay.objects.get(
                ip=get_client_ip(self.request), voting=self.voting)
        except VotingDelay.DoesNotExist:
            vd = VotingDelay(
                ip=get_client_ip(self.request), voting=self.voting,
                relieve_datetime=timezone.now()
            )
            vd.save()
            return vd

    def check_if_voted(self):
        request = self.request
        if request.user.is_authenticated():
            if request.user.id in [d['id'] for d in self.voting.voted_users.values('id')]:
                return True
        elif self.voting.id in request.session.get('voted_votings', []):
            return True
        vd = self.get_voting_delay()
        if timezone.now() < vd.relieve_datetime:
            return True
        return False


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class VotingView(VotingMixin, TemplateView):
    template_name = 'votes/voting.html'

    def update_vote_delay(self):
        vd = self.get_voting_delay()
        vd.relieve_datetime = timezone.now() + vd.delay
        vd.save()

    def check_if_vote_to_much(self, request):
        if self.check_if_voted():
            return True
        vd = self.get_voting_delay()
        relieve_date = vd.relieve_datetime or timezone.now()
        if timezone.now() - relieve_date > vd.delay:
            if vd.delay_level != 0:
                vd.delay_level = 0
                vd.save()
        else:
            vd.delay_level += 1
            vd.save()
        if relieve_date - timezone.now() > timedelta(0):
            return True
        return False

    def post(self, request, *args, **kwargs):
        if not self.check_if_vote_to_much(request):
            try:
                vote_n = int(request.POST.get('vote'))
                choice = self.voting.choices.get(order=vote_n)
            except (TypeError, Choice.DoesNotExist):
                kwargs['error'] = 'А проголосовать?'
                return self.get(request, *args, **kwargs)
            if request.user.is_authenticated():
                self.voting.voted_users.add(request.user)
            else:
                request.session['voted_votings'] = request.session.get('voted_votings', [])
                request.session['voted_votings'].append(self.voting.id)
            self.update_vote_delay()
            choice.votes += 1
            choice.save()
        return HttpResponseRedirect(reverse('votes_voting_results', kwargs=kwargs))

    def get_context_data(self, **kwargs):
        context = super(VotingView, self).get_context_data(**kwargs)
        try:
            context['voting'] = self.voting
            context['voted'] = self.check_if_voted()
        except Voting.DoesNotExist:
            raise Http404('Увы. Такого опроса не существует.')
        return context


class VotingResultsView(VotingMixin, TemplateView):
    template_name = 'votes/voting_results.html'

    def get_context_data(self, **kwargs):
        context = super(VotingResultsView, self).get_context_data(**kwargs)
        context['voted'] = context.get('voted') or self.check_if_voted()
        slug = self.kwargs['slug']
        try:
            context['voting'] = Voting.objects.get(slug=slug)
        except Voting.DoesNotExist:
            raise Http404('Увы. Такого опроса не существует.')
        return context
